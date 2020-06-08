import copy
import random

from ..pattern import Pattern
from ..key import Key
from ..scale import Scale
from ..constants import EVENT_NOTE, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_TRANSPOSE, \
    EVENT_CHANNEL, EVENT_OMIT, EVENT_GATE, EVENT_PHASE, EVENT_EVENT, EVENT_DEGREE, \
    EVENT_OCTAVE, EVENT_KEY, EVENT_SCALE, EVENT_VALUE, EVENT_OBJECT, EVENT_CONTROL, \
    EVENT_PRINT, EVENT_ACTION, EVENT_ADDRESS
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
        self.events = events

        next(self)

        self.timeline = timeline
        self.output_device = output_device
        self.phase_now = next(self.event[EVENT_PHASE])

        #------------------------------------------------------------------------
        # Reset our play position.
        #------------------------------------------------------------------------
        self.reset()

        self.note_offs = []
        self.finished = False

    def __str__(self):
        return "Track(pos = %d, note = %s, dur = %s, dur_now = %d, track = %s, control = %s))" % (
               self.pos, self.event[EVENT_NOTE], self.event[EVENT_DURATION],
               self.dur_now, self.event[EVENT_CHANNEL],
               self.event[EVENT_CONTROL] if EVENT_CONTROL in self.event else "-")

    def __next__(self):
        #----------------------------------------------------------------------
        # event is a dictionary of patterns. anything which is not a pattern
        # (eg, constant values) are turned into PConsts.
        #----------------------------------------------------------------------
        event = Pattern.value(self.events)

        event.setdefault(EVENT_NOTE, 60)
        event.setdefault(EVENT_TRANSPOSE, 0)
        event.setdefault(EVENT_DURATION, 1)
        event.setdefault(EVENT_AMPLITUDE, 64)
        event.setdefault(EVENT_CHANNEL, 0)
        event.setdefault(EVENT_OMIT, 0)
        event.setdefault(EVENT_GATE, 1.0)
        event.setdefault(EVENT_PHASE, 0.0)
        event.setdefault(EVENT_OCTAVE, 0)

        if EVENT_KEY in event:
            pass
        elif EVENT_SCALE in event:
            event[EVENT_KEY] = Key(0, event[EVENT_SCALE])
        else:
            event[EVENT_KEY] = Key(0, Scale.default)

        #----------------------------------------------------------------------
        # Turn constant values into patterns:
        #  - scalars becomes PConstant
        #  - array becomes PSequence
        #----------------------------------------------------------------------
        for key, value in list(event.items()):
            event[key] = Pattern.pattern(value)

        self.event = event

    def tick(self, time):
        #----------------------------------------------------------------------
        # process note_offs before we play the next note, else a repeated note
        # with gate = 1.0 will immediately be cancelled.
        #----------------------------------------------------------------------
        self.process_note_offs()

        try:
            if round(self.pos, 8) >= round(self.next_note + self.phase_now, 8):
                self.dur_now = next(self.event[EVENT_DURATION])
                self.phase_now = next(self.event[EVENT_PHASE])

                self.play()

                self.next_note += self.dur_now

                next(self)

        except StopIteration:
            if len(self.note_offs) == 0:
                self.finished = True

        self.pos += time

    def reset_to_beat(self):
        self.pos = round(self.pos)

    def reset(self):
        self.pos = 0
        self.dur_now = 0
        self.next_note = 0

    def play(self):
        values = {}
        for key, pattern in list(self.event.items()):
            # TODO: HACK!! to prevent stepping through dur twice (see 'tick' above')
            if key == EVENT_DURATION:
                value = self.dur_now
            elif key == EVENT_PHASE:
                value = self.phase_now
            else:
                value = next(pattern)
            values[key] = value

        #------------------------------------------------------------------------
        # print: Prints a value each time this event is triggered.
        #------------------------------------------------------------------------
        if EVENT_PRINT in values:
            print((values[EVENT_PRINT]))
            return

        #------------------------------------------------------------------------
        # action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if EVENT_ACTION in values:
            try:
                if EVENT_OBJECT in values:
                    object = values[EVENT_OBJECT]
                    values[EVENT_ACTION](object)
                else:
                    values[EVENT_ACTION]()
            except Exception as e:
                print(("Exception when handling scheduled action: %s" % e))
                import traceback
                traceback.print_exc()
                pass

            return

        #------------------------------------------------------------------------
        # control: Send a control value
        #------------------------------------------------------------------------
        if EVENT_CONTROL in values:
            log.debug("control (channel %d, control %d, value %d)",
                      values[EVENT_CHANNEL], values[EVENT_CONTROL], values[EVENT_VALUE])
            self.output_device.control(values[EVENT_CONTROL], values[EVENT_VALUE], values[EVENT_CHANNEL])
            return

        #------------------------------------------------------------------------
        # address: Send a value to an OSC endpoint
        #------------------------------------------------------------------------
        if EVENT_ADDRESS in values:
            self.output_device.send(values[EVENT_ADDRESS], values["params"])
            return

        #------------------------------------------------------------------------
        # note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        if EVENT_DEGREE in values:
            degree = values[EVENT_DEGREE]
            key = values[EVENT_KEY]
            octave = values[EVENT_OCTAVE]
            if not degree is None:
                #----------------------------------------------------------------------
                # handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                # addition transparently
                #----------------------------------------------------------------------
                try:
                    values[EVENT_NOTE] = [key[n] + (octave * 12) for n in degree]
                except:
                    values[EVENT_NOTE] = key[degree] + (octave * 12)

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, simply set our 'amp'
        # value to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
        if random.uniform(0, 1) < values[EVENT_OMIT]:
            values[EVENT_NOTE] = None

        if values[EVENT_NOTE] is None:
            #----------------------------------------------------------------------
            # Rest.
            #----------------------------------------------------------------------
            values[EVENT_NOTE] = 0
            values[EVENT_AMPLITUDE] = 0
            values[EVENT_GATE] = 0
        else:
            #----------------------------------------------------------------------
            # handle lists of notes (eg chords).
            # TODO: create a class which allows for scalars and arrays to handle
            # addition transparently.
            #
            # the below does not allow for values[EVENT_TRANSPOSE] to be an array,
            # for example.
            #----------------------------------------------------------------------
            try:
                values[EVENT_NOTE] = [note + values[EVENT_TRANSPOSE] for note in values[EVENT_NOTE]]
            except:
                values[EVENT_NOTE] += values[EVENT_TRANSPOSE]

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

                if (amp is not None and amp > 0) and (gate is not None and gate > 0):
                    self.output_device.note_on(note, amp, channel)

                    note_dur = self.dur_now * gate
                    self.schedule_note_off(self.next_note + note_dur + self.phase_now, note, channel)

    def schedule_note_off(self, time, note, channel):
        self.note_offs.append([time, note, channel])

    def process_note_offs(self):
        for n, note in enumerate(self.note_offs):
            # TODO: create a Note object to represent these note_off events
            if round(note[0], 8) <= round(self.pos, 8):
                index = note[1]
                channel = note[2]
                self.output_device.note_off(index, channel)
                self.note_offs.pop(n)
