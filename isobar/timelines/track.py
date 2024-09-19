from __future__ import annotations

import copy
import inspect
from typing import Union, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass

from .event import Event
if TYPE_CHECKING:
    from .timeline import Timeline
from ..pattern import Pattern, PSequence, PDict, PInterpolate
from ..constants import *
from ..exceptions import InvalidEventException
from ..util import midi_note_to_frequency
from ..io.output import OutputDevice
import logging

log = logging.getLogger(__name__)

@dataclass
class NoteOffEvent:
    timestamp: float
    note: int
    channel: int

class Track:
    def __init__(self,
                 timeline: Timeline,
                 max_event_count: Optional[int] = None,
                 interpolate: str = INTERPOLATION_NONE,
                 output_device: Optional[OutputDevice] = None,
                 remove_when_done: bool = True,
                 name: Optional[str] = None):
        """
        Args:
            timeline: The Timeline object that the track inhabits
            events: A dict, a PDict, or a Pattern that generates dicts.
            max_event_count: Optionally, the maximum number of events that will be executed. \
                             The Track will finish automatically once this number of events is complete.
            interpolate: Optional interpolation to impose on values, particularly for control tracks.
            output_device: Optional output device. Defaults to the Timeline's default_output_device.
            remove_when_done: If True, removes the Track from the Timeline when it finishes.
            name: Optional name for the track. If specified, can be used to update tracks in place by specifying \
                  its name when scheduling events on the Timeline.
        """
        #--------------------------------------------------------------------------------
        # Ensure that events is a pattern that generates a dict when it is iterated.
        #--------------------------------------------------------------------------------
        self.event_stream: Pattern = PDict({})
        self.timeline: Timeline = timeline
        self.current_time: float = 0.0
        self.next_event_time: float = sys.maxsize
        self.max_event_count: int = max_event_count
        self.current_event_count: int = 0
        self.name: str = name

        self.current_event: Optional[Event] = None
        self.next_event: Optional[Event] = None
        self.interpolating_event: Pattern = PSequence([], 0)

        self.output_device: OutputDevice = output_device
        self.interpolate: bool = interpolate

        self.note_offs: list[NoteOffEvent] = []
        self.is_muted: bool = False
        self.is_started: bool = False
        self.is_finished: bool = False
        self.remove_when_done: bool = remove_when_done
        self.on_event_callbacks: list[Callable] = []

    def __str__(self):
        if self.name:
            return "Track (name=%s, time=%.2f)" % (self.name, self.current_time)
        else:
            return "Track (time=%.2f)" % self.current_time

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

    def start(self,
              events: Union[dict, Pattern],
              interpolate: Optional[str] = None) -> None:
        """
        Begin executing the events on this track.

        Args:
            events: A dict, a PDict, or a Pattern that generates dicts.
        """
        if events is None:
            events = {}
        if isinstance(events, dict):
            events = PDict(events)
        self.event_stream = events

        self.is_started = True

        # Previously, this reset the counter to zero, but when re-scheduling a track that has
        # note-offs awaiting, this caused the existing notes to extend in duration.
        # Arguably it is more coherent to reset the time and adjust the note-off scheduling
        # accordingly, so may need to re-visit this.
        # self.current_time = 0.0

        self.next_event_time = self.current_time
        if interpolate is not None:
            self.interpolate = interpolate

    def update(self,
               events: Union[dict, Pattern],
               quantize: Optional[float] = None,
               delay: Optional[float] = None,
               interpolate: Optional[str] = None,
               count: Optional[int] = None):
        """
        Update the events that this Track produces.

        Args:
            events: A dict, a PDict, or a Pattern that generates dicts.
            quantize: An optional float that specifies the quantization that the update() should follow. \
                      quantize == 1 means that the update should happen on the next beat boundary.
            delay: Optional float specifying delay time applied to quantization
            interpolate: Optional interpolation mode
            count: Optional max_event_count
        """
        if quantize is None:
            quantize = self.timeline.defaults.quantize
        if delay is None:
            delay = self.timeline.defaults.delay
        if self.output_device is not None and self.output_device.added_latency_seconds > 0.0:
            delay += self.timeline.seconds_to_beats(self.output_device.added_latency_seconds)
        if count is not None:
            self.max_event_count = count

        #--------------------------------------------------------------------------------
        # Don't assign to events immediately, because in the case of quantized
        # updates, the existing stream should keep playing up until the moment
        # the track is updated.
        #--------------------------------------------------------------------------------
        if quantize == 0.0 and delay == 0.0:
            self.start(events, interpolate=interpolate)
        else:
            #--------------------------------------------------------------------------------
            # Schedule update event. Actions scheduled with schedule_action take place
            # before the track's tick() event is called.
            #--------------------------------------------------------------------------------
            self.timeline._schedule_action(function=lambda: self.start(events, interpolate=interpolate),
                                           quantize=quantize,
                                           delay=delay)

    @property
    def tick_duration(self) -> float:
        """
        Tick duration, in beats.
        """
        return self.timeline.tick_duration

    def process_note_offs(self):
        #----------------------------------------------------------------------
        # Process note_offs before we play the next note, else a repeated note
        # with gate = 1.0 will immediately be cancelled.
        #
        # Use round() to avoid scheduling issues arising from rounding errors.
        #----------------------------------------------------------------------
        for note_off in self.note_offs[:]:
            if round(note_off.timestamp, 8) <= round(self.current_time, 8):
                self.output_device.note_off(note_off.note, note_off.channel)
                self.note_offs.remove(note_off)

    def tick(self):
        """
        Step forward one tick.
        """

        if not self.is_started:
            return

        try:
            if self.interpolate is None or self.interpolate == INTERPOLATION_NONE:
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
                    interpolated_event = Event(interpolated_values, self.timeline.defaults, track=self)
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
                    event = Event(next(self.interpolating_event), self.timeline.defaults, track=self)
                    self.perform_event(event)

        except StopIteration:
            if len(self.note_offs) == 0:
                self.is_finished = True

        self.current_time += self.tick_duration

    def reset_to_beat(self):
        """
        Reset the track's time to the nearest integer.
        """
        self.current_time = round(self.current_time)

    def reset(self):
        """
        Rewind to the beginning of the pattern.
        """
        self.current_time = 0
        self.next_event_time = self.current_time

        for pattern in self.event_stream.values():
            try:
                pattern.reset()
            except AttributeError:
                # Event stream may contain constant values, in which case no reset is needed.
                pass

    def get_next_event(self) -> Event:
        """
        Retrieve the next event from the event stream dict.

        Returns:
            The next Event object

        Raises:
            StopIteration: If no more events are available, or the event count limit has been hit.

        """
        if self.event_stream is None:
            raise StopIteration

        # Allow for 0 to mean infinite events, for ease of use in live coding
        if self.max_event_count not in (None, 0) and self.current_event_count >= self.max_event_count:
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

        event = Event(event_values, self.timeline.defaults, track=self)
        self.current_event_count += 1

        return event

    def perform_event(self, event: Event):
        if not event.active:
            return
        if self.is_muted:
            return
        log.debug("Track: Executing event: %s" % event)

        #------------------------------------------------------------------------
        # Action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if event.type == EVENT_TYPE_ACTION:
            try:
                fn = event.action
                try:
                    fn_params = inspect.signature(fn).parameters
                    for key in event.args.keys():
                        if key not in fn_params:
                            raise Exception("Named argument not found in callback args: %s" % key)
                except ValueError:
                    #------------------------------------------------------------------------
                    # inspect.signature does not work on cython/pybind11 bindings, and
                    # raises a ValueError. In these cases, simply pass the arguments
                    # without validation.
                    #------------------------------------------------------------------------
                    pass
                event.action(**event.args)
            except StopIteration:
                raise StopIteration()
            except Exception as e:
                print("Exception when handling scheduled action: %s" % e)
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
        elif event.type == EVENT_TYPE_PATCH_CREATE:
            #------------------------------------------------------------------------
            # Action: Create patch
            #------------------------------------------------------------------------
            if not hasattr(self.output_device, "create"):
                raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
            params = dict((key, Pattern.value(value)) for key, value in event.params.items())
            if hasattr(event, "note"):
                notes = event.note if hasattr(event.note, '__iter__') else [event.note]

                for note in notes:
                    if note > 0:
                        # TODO: Should use None to denote rests
                        params["frequency"] = midi_note_to_frequency(note)
                        self.output_device.create(event.patch, params, output=event.output)
            else:
                self.output_device.create(event.patch, params, output=event.output)

        elif event.type == EVENT_TYPE_PATCH_SET or event.type == EVENT_TYPE_PATCH_TRIGGER:
            #------------------------------------------------------------------------
            # Action: Set patch's input(s) and/or trigger an event
            # If any of the params return None, the event is treated as a rest,
            # and the patch is not triggered.
            #------------------------------------------------------------------------
            event_is_rest = False
            for key, value in event.params.items():
                value = Pattern.value(value)
                if value is None:
                    event_is_rest = True
                else:
                    event.patch.set_input(key, value)

            if hasattr(event, "note"):
                event.patch.set_input("frequency", midi_note_to_frequency(event.note))

            if not event_is_rest:
                if event.type == EVENT_TYPE_PATCH_TRIGGER:
                    #------------------------------------------------------------------------
                    # Action: Trigger a patch
                    #------------------------------------------------------------------------
                    if not hasattr(self.output_device, "trigger"):
                        raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
                    params = dict((key, Pattern.value(value)) for key, value in event.params.items())
                    self.output_device.trigger(event.patch, event.trigger_name, event.trigger_value)

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
                    # Turn non-builtin objects into their string representations.
                    # We don't want to call repr() on numbers as it turns them into strings,
                    # which we don't want to happen in our resultant JSON.
                    # TODO: There absolutely must be a way to do this for all objects which are
                    #       non-builtins... ie, who are "class" instances rather than "type".
                    #
                    #       We could check dir(__builtins__), but for some reason, __builtins__ is
                    #       different here than it is outside of a module!?
                    #
                    #       Instead, go with the lame option of listing "primitive" types.
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
                        note_off_time = self.current_time + note_dur
                        note_off = NoteOffEvent(note_off_time, note, channel)
                        self.note_offs.append(note_off)
                if event.pitchbend is not None:
                    self.output_device.pitch_bend(event.pitchbend, channel)
        else:
            raise InvalidEventException("Invalid event type: %s" % event.type)

        if self.timeline.on_event_callback:
            self.timeline.on_event_callback(self, event)

        if self.on_event_callbacks:
            for callback in self.on_event_callbacks:
                callback(event)

    def stop(self):
        self.timeline.unschedule(self)

    def nudge(self, nudge_by: float):
        """
        Nudge the next event time by the specified offset. Useful for pushing different
        tracks in and out of phase, and for DJ-style beat matching.

        Args:
            nudge_by (float): The offset to nudge by, in beats. Can be negative.
        """
        self.next_event_time += nudge_by

    def mute(self) -> None:
        """
        Mutes the track. Subsequent events will be silenced until an unmute() is received.
        """
        self.is_muted = True

    def unmute(self) -> None:
        """
        Unmutes the track.
        """
        self.is_muted = False

    def add_event_callback(self, callback: Callable):
        """
        Callback to trigger when an event takes place.
        Useful for displaying GUI changes to reflect underlying events.

        The callback receives a single arg containing the Event.
        """
        self.on_event_callbacks.append(callback)

    def remove_event_callback(self, callback: Callable):
        """
        Remove an event callback.

        Args:
            callback: The callback to remove.
        """
        self.on_event_callbacks.remove(callback)
