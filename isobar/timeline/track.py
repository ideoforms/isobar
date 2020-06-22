import copy
import inspect

from ..pattern import Pattern, PSequence, PDict, PInterpolate
from ..key import Key
from ..scale import Scale
from ..constants import EVENT_NOTE, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_TRANSPOSE, \
    EVENT_CHANNEL, EVENT_GATE, EVENT_DEGREE, EVENT_PROGRAM_CHANGE, \
    EVENT_OCTAVE, EVENT_KEY, EVENT_SCALE, EVENT_VALUE, EVENT_ACTION_ARGS, EVENT_CONTROL, \
    EVENT_ACTION, EVENT_OSC_ADDRESS, EVENT_OSC_PARAMS, EVENT_TYPE, EVENT_PATCH, EVENT_PATCH_PARAMS
from ..constants import DEFAULT_EVENT_TRANSPOSE, DEFAULT_EVENT_AMPLITUDE, \
    DEFAULT_EVENT_CHANNEL, DEFAULT_EVENT_DURATION, DEFAULT_EVENT_GATE, DEFAULT_EVENT_OCTAVE
from ..constants import EVENT_TYPE_UNKNOWN, EVENT_TYPE_NOTE, EVENT_TYPE_ACTION, EVENT_TYPE_OSC, EVENT_TYPE_CONTROL, \
    EVENT_TYPE_PATCH, EVENT_TYPE_PROGRAM_CHANGE
from ..constants import INTERPOLATION_NONE, INTERPOLATION_LINEAR, INTERPOLATION_COSINE
from ..exceptions import InvalidEventException
import logging

log = logging.getLogger(__name__)

class Event:
    def __init__(self, event_values):
        event_values.setdefault(EVENT_CHANNEL, DEFAULT_EVENT_CHANNEL)
        event_values.setdefault(EVENT_DURATION, DEFAULT_EVENT_DURATION)
        event_values.setdefault(EVENT_GATE, DEFAULT_EVENT_GATE)
        event_values.setdefault(EVENT_AMPLITUDE, DEFAULT_EVENT_AMPLITUDE)
        event_values.setdefault(EVENT_OCTAVE, DEFAULT_EVENT_OCTAVE)
        event_values.setdefault(EVENT_TRANSPOSE, DEFAULT_EVENT_TRANSPOSE)
        event_values.setdefault(EVENT_SCALE, Scale.default)

        if EVENT_NOTE in event_values and EVENT_DEGREE in event_values:
            raise InvalidEventException("Cannot specify both note and degree")

        #------------------------------------------------------------------------
        # Note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        if EVENT_DEGREE in event_values:
            degree = event_values[EVENT_DEGREE]
            if degree is None:
                event_values[EVENT_NOTE] = None
            else:
                if EVENT_KEY in event_values:
                    key = event_values[EVENT_KEY]
                else:
                    key = Key(0, event_values[EVENT_SCALE])

                #----------------------------------------------------------------------
                # handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                # addition transparently
                #----------------------------------------------------------------------
                try:
                    event_values[EVENT_NOTE] = [key[n] for n in degree]
                except:
                    event_values[EVENT_NOTE] = key[degree]

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, set amplitude
        # to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
        if EVENT_NOTE in event_values:
            if event_values[EVENT_NOTE] is None:
                #----------------------------------------------------------------------
                # Rest.
                #----------------------------------------------------------------------
                event_values[EVENT_NOTE] = 0
                event_values[EVENT_AMPLITUDE] = 0
                event_values[EVENT_GATE] = 0
            else:
                #----------------------------------------------------------------------
                # Handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                #       addition transparently.
                #
                # The below does not allow for event_values[EVENT_TRANSPOSE] to be an array,
                # for example.
                #----------------------------------------------------------------------
                try:
                    event_values[EVENT_NOTE] = [note + event_values[EVENT_OCTAVE] * 12 + event_values[EVENT_TRANSPOSE] for note in event_values[EVENT_NOTE]]
                except:
                    event_values[EVENT_NOTE] += event_values[EVENT_OCTAVE] * 12 + event_values[EVENT_TRANSPOSE]

        #----------------------------------------------------------------------
        # Classify the event type.
        #----------------------------------------------------------------------
        if EVENT_ACTION in event_values:
            self.type = EVENT_TYPE_ACTION
            self.action = event_values[EVENT_ACTION]
            self.args = []
            if EVENT_ACTION_ARGS in event_values:
                self.args = [Pattern.value(value) for value in event_values[EVENT_ACTION_ARGS]]

        elif EVENT_PATCH in event_values:
            self.type = EVENT_TYPE_PATCH
            
        elif EVENT_CONTROL in event_values:
            self.type = EVENT_TYPE_CONTROL
            self.control = event_values[EVENT_CONTROL]
            self.value = event_values[EVENT_VALUE]
            self.channel = event_values[EVENT_CHANNEL]
            
        elif EVENT_PROGRAM_CHANGE in event_values:
            self.type = EVENT_TYPE_PROGRAM_CHANGE
            
        elif EVENT_OSC_ADDRESS in event_values:
            self.type = EVENT_TYPE_OSC
            
        elif EVENT_NOTE in event_values or EVENT_DEGREE in event_values:
            self.type = EVENT_TYPE_NOTE
            self.note = event_values[EVENT_NOTE]
            self.amplitude = event_values[EVENT_AMPLITUDE]
            self.gate = event_values[EVENT_GATE]
            self.channel = event_values[EVENT_CHANNEL]
            
        else:
            possible_event_types = [EVENT_NOTE, EVENT_DEGREE, EVENT_ACTION, EVENT_PATCH, EVENT_CONTROL, EVENT_PROGRAM_CHANGE, EVENT_OSC_ADDRESS]
            raise InvalidEventException("No event type specified (must provide one of %s)" % possible_event_types)
        
        self.duration = event_values[EVENT_DURATION]
        
        self.fields = event_values

class Track:
    def __init__(self, events, timeline, interpolate=INTERPOLATION_NONE, output_device=None):
        #--------------------------------------------------------------------------------
        # Ensure that events is a pattern that generates a dict when it is iterated.
        #--------------------------------------------------------------------------------
        if isinstance(events, dict):
            events = PDict(events)
        self.event_stream = events
        self.current_event = None
        self.next_event = None
        self.interpolating_event = PSequence([], 0)

        self.timeline = timeline
        self.output_device = output_device
        self.interpolate = interpolate

        self.current_time = 0
        self.next_event_time = 0
        self.note_offs = []
        self.is_finished = False

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
            # Have to be careful here.
            # formerly had `if self.current_event` ...
            # which would try to resolve the complete len of current_event:
            # https://stackoverflow.com/questions/1087135/boolean-value-of-objects-in-python
            # TODO: Think about __nonzero__ implementation for patterns?

            if self.interpolate is INTERPOLATION_NONE:
                if round(self.current_time, 8) >= round(self.next_event_time, 8):
                    self.current_event = self.get_next_event()
                    self.perform_event(self.current_event)
                    self.next_event_time += float(self.current_event.duration)
            else:
                try:
                    interpolated_values = Event(next(self.interpolating_event))
                    self.perform_event(interpolated_values)
                except StopIteration:
                    is_first_event = False
                    if self.next_event is None:
                        self.next_event = self.get_next_event()
                        is_first_event = True
                    self.current_event = self.next_event
                    self.next_event = self.get_next_event()

                    if self.current_event.type != EVENT_TYPE_CONTROL:
                        raise InvalidEventException("Interpolation is only valid for control event")

                    interpolating_event_fields = copy.copy(self.current_event.fields)
                    duration = self.current_event.duration
                    duration_ticks = duration * self.timeline.ticks_per_beat
                    for key, value in self.current_event.fields.items():
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
                    interpolated_values = Event(next(self.interpolating_event))
                    self.perform_event(interpolated_values)

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
            pattern.reset()

    def get_next_event(self):
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
        
        event = Event(event_values)

        return event

    def perform_event(self, event):
        #------------------------------------------------------------------------
        # Action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if event.type == EVENT_TYPE_ACTION:
            try:
                fn = event.action
                args = event.args
                fn_params = inspect.signature(fn).parameters
                kwargs = dict((key, value) for key, value in event.fields.items() if key in fn_params)
                event.action(*args, **kwargs)
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

        elif event.type == EVENT_TYPE_PATCH:
            if not hasattr(self.output_device, "create"):
                raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
            params = event.patch_params if EVENT_PATCH_PARAMS in event.fields else {}
            params = dict((key, Pattern.value(value)) for key, value in params.items())
            self.output_device.create(event.patch, params)

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
                        name = type(value).__name__
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
                        self.schedule_note_off(self.next_event_time + note_dur, note, channel)
        else:
            raise InvalidEventException("Invalid event type: %s" % event.type)

    def schedule_note_off(self, time, note, channel):
        self.note_offs.append([time, note, channel])
