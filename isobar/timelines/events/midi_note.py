from __future__ import annotations
from dataclasses import dataclass

from .midi import MidiEvent
from ...constants import EVENT_DEGREE, EVENT_NOTE, EVENT_KEY, EVENT_OCTAVE, EVENT_TRANSPOSE, EVENT_PITCHBEND, EVENT_AMPLITUDE, EVENT_GATE, EVENT_TYPE_NOTE
from ...exceptions import InvalidEventException
from ...key import Key
from ..midi_note import MidiNoteInstance

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


@dataclass
class NoteOffEvent:
    timestamp: float
    note: int
    channel: int


class MidiNoteEvent(MidiEvent):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        if EVENT_NOTE in event_values and EVENT_DEGREE in event_values:
            raise InvalidEventException("Cannot specify both note and degree")

        #------------------------------------------------------------------------
        # Note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        if EVENT_DEGREE in event_values:
            degree = event_values[EVENT_DEGREE]
            if degree is None:
                #------------------------------------------------------------------------
                # Rest
                #------------------------------------------------------------------------
                event_values[EVENT_NOTE] = None
            else:
                #--------------------------------------------------------------------------------
                # Tolerate float degrees.
                # This may need revisiting for tunings that permit sub-semitone values.
                #--------------------------------------------------------------------------------
                try:
                    degree = [int(degree) for degree in degree]
                except:
                    degree = int(degree)

                key = event_values[EVENT_KEY]
                if isinstance(key, str):
                    key = Key(key)

                #--------------------------------------------------------------------------------
                # Handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                #       addition transparently
                #--------------------------------------------------------------------------------
                try:
                    event_values[EVENT_NOTE] = [key[n] for n in degree]
                except TypeError:
                    event_values[EVENT_NOTE] = key[degree]

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, set amplitude
        # to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
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
            transpose = int(event_values[EVENT_OCTAVE]) * 12 + int(event_values[EVENT_TRANSPOSE])
            try:
                event_values[EVENT_NOTE] = [int(note) + transpose for note in event_values[EVENT_NOTE]]
            except TypeError:
                event_values[EVENT_NOTE] += transpose

        self.type = EVENT_TYPE_NOTE

        self.note = event_values[EVENT_NOTE]
        self.amplitude = event_values[EVENT_AMPLITUDE]
        self.gate = event_values[EVENT_GATE]

        self.pitchbend = event_values[EVENT_PITCHBEND]

    def perform(self) -> bool:
        #----------------------------------------------------------------------
        # event_did_fire is set to True if the event includes one or more
        # notes whose amplitude is greater than zero.
        #----------------------------------------------------------------------
        event_did_fire = False

        #----------------------------------------------------------------------
        # note_on: Standard (MIDI) type of device
        # If the amplitude is None or 0, this is a rest.
        #----------------------------------------------------------------------
        if type(self.amplitude) is tuple or (self.amplitude is not None and self.amplitude > 0):
            notes = self.note if hasattr(self.note, '__iter__') else [self.note]

            #----------------------------------------------------------------------
            # Allow for arrays of amp, gate etc, to handle chords properly.
            #----------------------------------------------------------------------
            for index, note in enumerate(notes):
                amplitude = self.amplitude[index % len(self.amplitude)] if isinstance(self.amplitude, tuple) else self.amplitude
                amplitude = int(amplitude)
                channel = self.channel[index % len(self.channel)] if isinstance(self.channel, tuple) else self.channel
                gate = self.gate[index % len(self.gate)] if isinstance(self.gate, tuple) else self.gate

                if (amplitude is not None and amplitude > 0) and (gate is not None and gate > 0):
                    event_did_fire = True
                    duration = self.duration * gate

                    note = MidiNoteInstance(note=note,
                                            amplitude=amplitude,
                                            channel=channel,
                                            timestamp=self.track.current_time,
                                            duration=duration)
                    self.track.schedule_note(note)

            if self.pitchbend is not None:
                self.output_device.pitch_bend(self.pitchbend, channel)

        return event_did_fire