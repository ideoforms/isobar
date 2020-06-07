from ..midinote import MidiNote

import mido
import logging

log = logging.getLogger(__name__)

class MidiFileIn:
    """ Read events from a MIDI file.
        Requires mido. """

    def __init__(self, filename):
        self.filename = filename

    def read(self, quantize=0.25):
        midi_reader = mido.MidiFile(self.filename)
        note_tracks = list(filter(lambda track: any(message.type == 'note_on' for message in track), midi_reader.tracks))
        if not note_tracks:
            raise ValueError("Could not find any tracks with note data")

        #------------------------------------------------------------------------
        # TODO: Support for multiple tracks
        #------------------------------------------------------------------------
        track = note_tracks[0]

        notes = []
        offset = 0
        for event in track:
            if event.type == 'note_on' and event.velocity > 0:
                #------------------------------------------------------------------------
                # Found a note_on event.
                #------------------------------------------------------------------------
                offset += event.time / 96.0
                note = MidiNote(event.note, event.velocity, offset)
                notes.append(note)
                print("found note on for note %d - location %f, time %f" % (note.pitch, note.location, event.time))
                print("offset now %f" % offset)
            elif event.type == 'note_off' or (event.type == 'note_on' and event.velocity == 0):
                #------------------------------------------------------------------------
                # Found a note_off event.
                #------------------------------------------------------------------------
                offset += event.time / 96.0
                for note in reversed(notes):
                    if note.pitch == event.note:
                        note.duration = offset - note.location
                        print("found note off for note %d - location %f, offset %f, duration %f" % (note.pitch, note.location, offset, note.duration))
                        break

                print("offset now %f" % offset)

        for note in notes:
            if quantize:
                # note.location = round(note.location / quantize) * quantize
                # note.duration = round(note.duration / quantize) * quantize
                pass
            print("Note %d (vel = %d, dur = %f)" % (note.pitch, note.velocity, note.duration))

        #------------------------------------------------------------------------
        # Construct a sequence which honours chords and relative lengths.
        # First, group all notes by their starting time.
        #------------------------------------------------------------------------
        notes_by_time = {}
        for note in notes:
            log.debug("(%.2f) %d/%d, %s" % (note.location, note.pitch, note.velocity, note.duration))
            location = note.location
            if location in notes_by_time:
                notes_by_time[location].append(note)
            else:
                notes_by_time[location] = [note]

        note_dict = {
            "note": [],
            "amp": [],
            "gate": [],
            "dur": []
        }
        for n in notes_by_time:
            print("%s - %s" % (n, notes_by_time[n]))

        #------------------------------------------------------------------------
        # Next, iterate through groups of notes chronologically, figuring out
        # appropriate parameters for duration (eg, inter-note distance) and
        # gate (eg, proportion of distance note extends across).
        #------------------------------------------------------------------------
        times = sorted(notes_by_time.keys())
        for i in range(len(times)):
            time = times[i]
            notes = notes_by_time[time]

            #------------------------------------------------------------------------
            # Our duration is always determined by the time of the next note event.
            # If a next note does not exist, this is the last note of the sequence;
            # use the maximal length of note currently playing (assuming a chord)
            #------------------------------------------------------------------------
            if i < len(times) - 1:
                next_time = times[i + 1]
            else:
                next_time = time + max([note.duration for note in notes])

            dur = next_time - time
            note_dict["dur"].append(dur)

            if len(notes) > 1:
                note_dict["note"].append(tuple(note.pitch for note in notes))
                note_dict["amp"].append(tuple(note.velocity for note in notes))
                note_dict["gate"].append(tuple(note.duration / dur for note in notes))
            else:
                note = notes[0]
                note_dict["note"].append(note.pitch)
                note_dict["amp"].append(note.velocity)
                note_dict["gate"].append(note.duration / dur)

        return note_dict
