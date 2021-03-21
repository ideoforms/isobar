import copy
import math
import inspect

from .event import Event
from ..pattern import Pattern, PSequence, PDict, PInterpolate
from ..constants import *
from ..exceptions import InvalidEventException
import logging

log = logging.getLogger(__name__)

class Track:
    def __init__(self, timeline, events, max_event_count=None, interpolate=INTERPOLATION_NONE,
                 output_device=None, remove_when_done=True):
        #--------------------------------------------------------------------------------
        # Ensure that events is a pattern that generates a dict when it is iterated.
        #--------------------------------------------------------------------------------
        self.event_stream = {}
        self.timeline = timeline
        self.current_time = 0
        self.next_event_time = 0
        self.max_event_count = max_event_count
        self.current_event_count = 0

        self.update(events)
        self.current_event = None
        self.next_event = None
        self.interpolating_event = PSequence([], 0)

        self.output_device = output_device
        self.interpolate = interpolate

        self.note_offs = []
        self.is_finished = False
        self.remove_when_done = remove_when_done

    def __getattr__(self, item):
        return self.event_stream[item]

    def __setattr__(self, item, value):
        #--------------------------------------------------------------------------------
        # Benign magic so that you can do things like
        #
        #    track.note = 64
        #
        # Note that this will only work when the track has been created with a dict
        # of key-value pairs (rather than a pattern that will itself generate dicts.)
        #--------------------------------------------------------------------------------
        if item != "event_stream" and isinstance(self.event_stream, PDict) and item in ALL_EVENT_PARAMETERS:
            self.event_stream[item] = value
        else:
            super().__setattr__(item, value)

    def __delattr__(self, item):
        if item != "event_stream" and isinstance(self.event_stream, PDict) and item in ALL_EVENT_PARAMETERS:
            del self.event_stream[item]
        else:
            super().__delattr__(item)

    def update(self, events, quantize=None):
        """
        Update the events that this Track produces.

        Args:
            events: A dict, a PDict, or a Pattern that generates dicts.
        """
        if events is None:
            events = {}
        if isinstance(events, dict):
            events = PDict(events)

        if quantize is None:
            quantize = self.timeline.defaults.quantize

        if quantize:
            self.next_event_time = quantize * math.ceil(float(self.current_time) / quantize)
        else:
            self.next_event_time = self.current_time

        self.event_stream = events

    def __str__(self):
        return "Track (pos = %d)" % self.current_time

    @property
    def tick_duration(self):
        return self.timeline.tick_duration

    def tick(self):
        """
        Step forward one tick.

        Args:
            tick_duration (float): Duration, in beats.
        """

        #----------------------------------------------------------------------
        # Process note_offs before we play the next note, else a repeated note
        # with gate = 1.0 will immediately be cancelled.
        #----------------------------------------------------------------------
        for n, note in enumerate(self.note_offs[:]):
            # TODO: Use a MidiNote object to represent these note_off events
            if round(note[0], 8) <= round(self.current_time, 8):
                index = note[1]
                channel = note[2]
                self.output_device.note_off(index, channel)
                self.note_offs.remove(note)

        try:
            if self.interpolate is INTERPOLATION_NONE:
                if round(self.current_time, 8) >= round(self.next_event_time, 8):
                    while round(self.current_time, 8) >= round(self.next_event_time, 8):
                        #--------------------------------------------------------------------------------
                        # Retrieve the next event.
                        # If no more events are available, this raises StopIteration.
                        #--------------------------------------------------------------------------------
                        self.current_event = self.get_next_event()
                        self.next_event_time += float(self.current_event.duration)

                    #--------------------------------------------------------------------------------
                    # Perform the event.
                    #--------------------------------------------------------------------------------
                    self.perform_event(self.current_event)
            else:
                #--------------------------------------------------------------------------------
                # Track has interpolation enabled.
                # Interpolation is done by wrapping the evolving event in an
                # interpolating_event, which generates a new value each tick until it is
                # exhausted.
                #--------------------------------------------------------------------------------
                try:
                    interpolated_values = next(self.interpolating_event)
                    interpolated_event = Event(interpolated_values, self.timeline.defaults)
                    self.perform_event(interpolated_event)
                except StopIteration:
                    is_first_event = False
                    if self.next_event is None:
                        #--------------------------------------------------------------------------------
                        # The current and next events are needed to perform interpolation.
                        # No events have yet been obtained, so query the current and next events off
                        # the stack.
                        #--------------------------------------------------------------------------------
                        self.next_event = self.get_next_event()
                        is_first_event = True

                    self.current_event = self.next_event
                    self.next_event = self.get_next_event()

                    #--------------------------------------------------------------------------------
                    # Special case to handle zero-duration events: continue to pop new
                    # events from the pattern.
                    #--------------------------------------------------------------------------------
                    while int(self.current_event.duration * self.timeline.ticks_per_beat) <= 0:
                        self.current_event = self.next_event
                        self.next_event = self.get_next_event()

                    if self.current_event.type != EVENT_TYPE_CONTROL or self.next_event.type != EVENT_TYPE_CONTROL:
                        raise InvalidEventException("Interpolation is only valid for control event")

                    interpolating_event_fields = copy.copy(self.current_event.fields)
                    duration = self.current_event.duration
                    duration_ticks = duration * self.timeline.ticks_per_beat
                    for key, value in self.current_event.fields.items():
                        #--------------------------------------------------------------------------------
                        # Create a new interpolating_event with patterns for each parameter to
                        # interpolate.
                        #--------------------------------------------------------------------------------
                        if key == EVENT_TYPE or key == EVENT_DURATION:
                            continue
                        if type(value) is not float and type(value) is not int:
                            continue
                        interpolating_event_fields[key] = PInterpolate(PSequence([self.current_event.fields[key],
                                                                                  self.next_event.fields[key]], 1),
                                                                       duration_ticks,
                                                                       self.interpolate)

                    self.interpolating_event = PDict(interpolating_event_fields)
                    if not is_first_event:
                        next(self.interpolating_event)
                    event = Event(next(self.interpolating_event), self.timeline.defaults)
                    self.perform_event(event)

        except StopIteration:
            if len(self.note_offs) == 0:
                self.is_finished = True

        self.current_time += self.tick_duration

    def reset_to_beat(self):
        self.current_time = round(self.current_time)

    def reset(self):
        self.current_time = 0
        self.next_event_duration = 0
        self.next_event_time = 0

        for pattern in self.event_stream.values():
            try:
                pattern.reset()
            except AttributeError:
                # Event stream may contain constant values, in which case no reset is needed.
                pass

    def get_next_event(self):
        """
        Retrieve the next event from the event stream dict.

        Returns:
            The next Event object

        Raises:
            StopIteration: If no more events are available, or the event count limit has been hit.

        """
        if self.event_stream is None:
            raise StopIteration

        if self.max_event_count is not None and self.current_event_count >= self.max_event_count:
            raise StopIteration

        #------------------------------------------------------------------------
        # Iterate to the next event.
        #  - If self.events is a PDict, this iterates over each of the keys
        #    and returns a dictionary.
        #  - If self.events is a pattern which returns a dict, the next value
        #    is iterated.
        # Take a copy to avoid modifying the original.
        #------------------------------------------------------------------------
        event_values = next(self.event_stream)
        event_values = copy.copy(event_values)

        event = Event(event_values, self.timeline.defaults)
        self.current_event_count += 1

        return event

    def perform_event(self, event):
        if not event.active:
            return

        #------------------------------------------------------------------------
        # Action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if event.type == EVENT_TYPE_ACTION:
            try:
                fn = event.action
                fn_params = inspect.signature(fn).parameters
                for key in event.args.keys():
                    if key not in fn_params:
                        raise Exception("Named argument not found in callback args: %s" % key)
                event.action(**event.args)
            except StopIteration:
                raise StopIteration()
            except Exception as e:
                print(("Exception when handling scheduled action: %s" % e))
                import traceback
                traceback.print_exc()
                pass

        #------------------------------------------------------------------------
        # Control: Send a control value
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_CONTROL:
            log.debug("Control (channel %d, control %d, value %d)",
                      event.channel, event.control, event.value)
            self.output_device.control(event.control, event.value, event.channel)

        #------------------------------------------------------------------------
        # Program change
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_PROGRAM_CHANGE:
            log.debug("Program change (channel %d, program %d)",
                      event.channel, event.program_change)
            self.output_device.program_change(event.program_change, event.channel)

        #------------------------------------------------------------------------
        # address: Send a value to an OSC endpoint
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_OSC:
            self.output_device.send(event.osc_address, event.osc_params)

        #------------------------------------------------------------------------
        # SuperCollider synth
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_SUPERCOLLIDER:
            self.output_device.create(event.synth_name, event.synth_params)

        #------------------------------------------------------------------------
        # SignalFlow patch
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_PATCH:
            if not hasattr(self.output_device, "create"):
                raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
            params = dict((key, Pattern.value(value)) for key, value in event.params.items())
            self.output_device.create(event.patch, params)

        elif event.type == EVENT_TYPE_TRIGGER:
            if not hasattr(self.output_device, "trigger"):
                raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
            params = dict((key, Pattern.value(value)) for key, value in event.params.items())
            self.output_device.trigger(event.patch, params)

        #------------------------------------------------------------------------
        # Note: Classic MIDI note
        #------------------------------------------------------------------------
        elif event.type == EVENT_TYPE_NOTE:
            #----------------------------------------------------------------------
            # event: Certain devices (eg Socket IO) handle generic events,
            #        rather than note_on/note_off. (Should probably have to
            #        register for this behaviour rather than happening magically...)
            #----------------------------------------------------------------------
            if hasattr(self.output_device, "event") and callable(getattr(self.output_device, "event")):
                d = copy.copy(event)
                for key, value in list(d.items()):
                    #------------------------------------------------------------------------
                    # turn non-builtin objects into their string representations.
                    # we don't want to call repr() on numbers as it turns them into strings,
                    # which we don't want to happen in our resultant JSON.
                    # TODO: there absolutely must be a way to do this for all objects which are
                    #       non-builtins... ie, who are "class" instances rather than "type".
                    #
                    #       we could check dir(__builtins__), but for some reason, __builtins__ is
                    #       different here than it is outside of a module!?
                    #
                    #       instead, go with the lame option of listing "primitive" types.
                    #------------------------------------------------------------------------
                    if type(value) not in (int, float, bool, str, list, dict, tuple):
                        value = repr(value)
                        d[key] = value

                self.output_device.event(d)
                return

            #----------------------------------------------------------------------
            # note_on: Standard (MIDI) type of device
            #----------------------------------------------------------------------
            if type(event.amplitude) is tuple or event.amplitude > 0:
                # TODO: pythonic duck-typing approach might be better
                # TODO: doesn't handle arrays of amp, channel event, etc
                notes = event.note if hasattr(event.note, '__iter__') else [event.note]

                #----------------------------------------------------------------------
                # Allow for arrays of amp, gate etc, to handle chords properly.
                # Caveat: Things will go horribly wrong for an array of amp/gate event
                # shorter than the number of notes.
                #----------------------------------------------------------------------
                for index, note in enumerate(notes):
                    amp = event.amplitude[index] if isinstance(event.amplitude, tuple) else event.amplitude
                    channel = event.channel[index] if isinstance(event.channel, tuple) else event.channel
                    gate = event.gate[index] if isinstance(event.gate, tuple) else event.gate
                    # TODO: Add an EVENT_SUSTAIN that allows absolute note lengths to be specified

                    if (amp is not None and amp > 0) and (gate is not None and gate > 0):
                        self.output_device.note_on(note, amp, channel)

                        note_dur = event.duration * gate
                        self.schedule_note_off(self.current_time + note_dur, note, channel)
        else:
            raise InvalidEventException("Invalid event type: %s" % event.type)

    def schedule_note_off(self, time, note, channel):
        self.note_offs.append([time, note, channel])

    def stop(self):
        self.timeline.unschedule(self)