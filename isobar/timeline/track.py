import copy
import random

from ..pattern import Pattern
from ..key import Key
from ..scale import Scale
from ..constants import EVENT_NOTE, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_TRANSPOSE, \
    EVENT_CHANNEL, EVENT_GATE, EVENT_EVENT, EVENT_DEGREE, \
    EVENT_OCTAVE, EVENT_KEY, EVENT_SCALE, EVENT_VALUE, EVENT_ACTION_OBJECT, EVENT_CONTROL, \
    EVENT_ACTION, EVENT_OSC_ADDRESS, EVENT_OSC_PARAMS, EVENT_TYPE
from ..constants import DEFAULT_EVENT_TRANSPOSE, DEFAULT_EVENT_AMPLITUDE, \
    DEFAULT_EVENT_CHANNEL, DEFAULT_EVENT_DURATION, DEFAULT_EVENT_GATE, DEFAULT_EVENT_OCTAVE
from ..constants import EVENT_TYPE_UNKNOWN, EVENT_TYPE_NOTE, EVENT_TYPE_ACTION, EVENT_TYPE_OSC, EVENT_TYPE_CONTROL
from ..exceptions import InvalidEventException
import logging

log = logging.getLogger(__name__)

class Track:
    def __init__(self, events={}, timeline=None, output_device=None):
        #----------------------------------------------------------------------
        # evaluate in case we have a pattern which gives us an event
        # eg: PSeq([ { EVENT_NOTE : 20, EVENT_DURATION : 0.5 }, { EVENT_NOTE : 50, EVENT_DURATION : PWhite(0, 2) } ])
        #
        # is this ever even necessary?
        #----------------------------------------------------------------------
        # self.events = Pattern.pattern(events)
        self.schedule(events)

        # TODO: Is this needed?
        self.timeline = timeline
        self.output_device = output_device

        self.current_time = 0
        self.next_event_time = 0
        self.note_offs = []
        self.is_finished = False

    def __str__(self):
        return "Track (pos = %d)" % self.current_time

    def schedule(self, events):
        events.setdefault(EVENT_CHANNEL, DEFAULT_EVENT_CHANNEL)
        events.setdefault(EVENT_DURATION, DEFAULT_EVENT_DURATION)
        events.setdefault(EVENT_GATE, DEFAULT_EVENT_GATE)
        events.setdefault(EVENT_AMPLITUDE, DEFAULT_EVENT_AMPLITUDE)
        events.setdefault(EVENT_OCTAVE, DEFAULT_EVENT_OCTAVE)
        events.setdefault(EVENT_TRANSPOSE, DEFAULT_EVENT_TRANSPOSE)
        events.setdefault(EVENT_SCALE, Scale.default)

        if EVENT_NOTE in events and EVENT_DEGREE in events:
            raise InvalidEventException("Cannot specify both note and degree")

        #----------------------------------------------------------------------
        # Turn constant values into patterns:
        #  - scalars becomes PConstant
        #  - array becomes PSequence
        #----------------------------------------------------------------------
        for key, value in list(events.items()):
            events[key] = Pattern.pattern(value)

        self.events = events

    def tick(self, tick_duration):
        #----------------------------------------------------------------------
        # process note_offs before we play the next note, else a repeated note
        # with gate = 1.0 will immediately be cancelled.
        #----------------------------------------------------------------------
        self.process_note_offs()

        try:
            if round(self.current_time, 8) >= round(self.next_event_time, 8):
                event = self.get_next_event()
                self.perform_event(event)
                self.next_event_time += event[EVENT_DURATION]

        except StopIteration:
            if len(self.note_offs) == 0:
                self.is_finished = True

        self.current_time += tick_duration

    def reset_to_beat(self):
        self.current_time = round(self.current_time)

    def reset(self):
        self.current_time = 0
        self.next_event_duration = 0
        self.next_event_time = 0

    def get_next_event(self):
        values = {}
        for key, pattern in self.events.items():
            values[key] = next(pattern)

        #------------------------------------------------------------------------
        # Note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        if EVENT_DEGREE in values:
            degree = values[EVENT_DEGREE]
            if degree is None:
                values[EVENT_NOTE] = None
            else:
                if EVENT_KEY in values:
                    key = values[EVENT_KEY]
                else:
                    key = Key(0, values[EVENT_SCALE])

                #----------------------------------------------------------------------
                # handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                # addition transparently
                #----------------------------------------------------------------------
                try:
                    values[EVENT_NOTE] = [key[n] for n in degree]
                except:
                    values[EVENT_NOTE] = key[degree]

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, set amplitude
        # to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
        if EVENT_NOTE in values:
            if values[EVENT_NOTE] is None:
                #----------------------------------------------------------------------
                # Rest.
                #----------------------------------------------------------------------
                values[EVENT_NOTE] = 0
                values[EVENT_AMPLITUDE] = 0
                values[EVENT_GATE] = 0
            else:
                #----------------------------------------------------------------------
                # Handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                #       addition transparently.
                #
                # The below does not allow for values[EVENT_TRANSPOSE] to be an array,
                # for example.
                #----------------------------------------------------------------------
                try:
                    values[EVENT_NOTE] = [note + values[EVENT_OCTAVE] * 12 + values[EVENT_TRANSPOSE] for note in values[EVENT_NOTE]]
                except:
                    values[EVENT_NOTE] += values[EVENT_OCTAVE] * 12 + values[EVENT_TRANSPOSE]

        #----------------------------------------------------------------------
        # Classify the event type.
        #----------------------------------------------------------------------
        if EVENT_ACTION in values:
            values[EVENT_TYPE] = EVENT_TYPE_ACTION
        elif EVENT_CONTROL in values:
            values[EVENT_TYPE] = EVENT_TYPE_CONTROL
        elif EVENT_OSC_ADDRESS in values:
            values[EVENT_TYPE] = EVENT_TYPE_OSC
        elif EVENT_NOTE in values or EVENT_DEGREE in values:
            values[EVENT_TYPE] = EVENT_TYPE_NOTE
        else:
            values[EVENT_TYPE] = EVENT_TYPE_UNKNOWN

        return values

    def perform_event(self, values):
        #------------------------------------------------------------------------
        # Action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if values[EVENT_TYPE] == EVENT_TYPE_ACTION:
            try:
                if EVENT_ACTION_OBJECT in values:
                    object = values[EVENT_ACTION_OBJECT]
                    values[EVENT_ACTION](object)
                else:
                    values[EVENT_ACTION]()
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
        elif values[EVENT_TYPE] == EVENT_TYPE_CONTROL:
            log.debug("Control (channel %d, control %d, value %d)",
                      values[EVENT_CHANNEL], values[EVENT_CONTROL], values[EVENT_VALUE])
            self.output_device.control(values[EVENT_CONTROL], values[EVENT_VALUE], values[EVENT_CHANNEL])

        #------------------------------------------------------------------------
        # address: Send a value to an OSC endpoint
        #------------------------------------------------------------------------
        elif values[EVENT_TYPE] == EVENT_TYPE_OSC:
            self.output_device.send(values[EVENT_OSC_ADDRESS], values[EVENT_OSC_PARAMS])

        elif values[EVENT_TYPE] == EVENT_TYPE_NOTE:
            #----------------------------------------------------------------------
            # event: Certain devices (eg Socket IO) handle generic events,
            #        rather than note_on/note_off. (Should probably have to
            #        register for this behaviour rather than happening magically...)
            #----------------------------------------------------------------------
            if hasattr(self.output_device, "event") and callable(getattr(self.output_device, "event")):
                d = copy.copy(values)
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
            if type(values[EVENT_AMPLITUDE]) is tuple or values[EVENT_AMPLITUDE] > 0:
                # TODO: pythonic duck-typing approach might be better
                # TODO: doesn't handle arrays of amp, channel values, etc
                notes = values[EVENT_NOTE] if hasattr(values[EVENT_NOTE], '__iter__') else [values[EVENT_NOTE]]

                #----------------------------------------------------------------------
                # Allow for arrays of amp, gate etc, to handle chords properly.
                # Caveat: Things will go horribly wrong for an array of amp/gate values
                # shorter than the number of notes.
                #----------------------------------------------------------------------
                for index, note in enumerate(notes):
                    amp = values[EVENT_AMPLITUDE][index] if isinstance(values[EVENT_AMPLITUDE], tuple) else values[EVENT_AMPLITUDE]
                    channel = values[EVENT_CHANNEL][index] if isinstance(values[EVENT_CHANNEL], tuple) else values[EVENT_CHANNEL]
                    gate = values[EVENT_GATE][index] if isinstance(values[EVENT_GATE], tuple) else values[EVENT_GATE]
                    # TODO: Add an EVENT_SUSTAIN that allows absolute note lengths to be specified

                    if (amp is not None and amp > 0) and (gate is not None and gate > 0):
                        self.output_device.note_on(note, amp, channel)

                        note_dur = values[EVENT_DURATION] * gate
                        self.schedule_note_off(self.next_event_time + note_dur, note, channel)
        else:
            raise InvalidEventException("Invalid event")

    def schedule_note_off(self, time, note, channel):
        self.note_offs.append([time, note, channel])

    def process_note_offs(self):
        for n, note in enumerate(self.note_offs[:]):
            # TODO: create a Note object to represent these note_off events
            if round(note[0], 8) <= round(self.current_time, 8):
                index = note[1]
                channel = note[2]
                self.output_device.note_off(index, channel)
                self.note_offs.remove(note)
