#------------------------------------------------------------------------
# absolute_import is needed so we can import MidiUtil without
# filename clash with isobar/io/midi.py.
#------------------------------------------------------------------------

from isobar.note import *
from isobar.pattern.core import *

import logging
log = logging.getLogger(__name__)

class Note:
    def __init__(self, pitch, velocity, location, duration = None):
        # pitch = MIDI 0..127
        self.pitch = pitch
        # velocity = MIDI 0..127
        self.velocity = velocity
        # location in time, beats
        self.location = location
        # duration in time, beats
        self.duration = duration

class MidiFileIn:
    """ Read events from a MIDI file.
        Requires ... """

    def __init__(self, filename):
        self.filename = filename

        # requires python-midi
        import midi

    def read_note_list(self, filename, quantize = 0.25):
        reader = midi.FileReader()
        data = reader.read(file(self.filename))

        notes = []
        for track in data:
            track.make_ticks_abs()
            for event in [event for event in track if isinstance(event, midi.events.NoteEvent)]:
                location = event.tick / 96.0
                if isinstance(event, midi.events.NoteOnEvent) and event.velocity > 0:
                    log.info("(%.2f beats) %s. \t(note = %d, velocity = %d)" % (location, miditoname(event.pitch), event.pitch, event.velocity))

                    #------------------------------------------------------------------------
                    # anomaly: sometimes a midi file might have a note on when the previous
                    # note has not finished; end it automatically
                    #------------------------------------------------------------------------
                    for note in reversed(notes):
                        if note.pitch == event.pitch:
                            if not note.duration:
                                log.warn("note-on found without note-off; cancelling previous note")
                                duration = location - note.location
                                note.duration = duration
                                if duration == 0:
                                    log.warn("*** DURATION OF ZERO??")
                            break

                    note = Note(event.pitch, event.velocity, location)
                    notes.append(note)

                #------------------------------------------------------------------------
                # A NoteOn event with velocity == 0 also acts as a NoteOff.
                #------------------------------------------------------------------------
                if isinstance(event, midi.events.NoteOffEvent) or (isinstance(event, midi.events.NoteOnEvent) and event.velocity == 0):
                    log.debug("(%.2f beats) %s off \t(note = %d, velocity = %d)" % (location, miditoname(event.pitch), event.pitch, event.velocity))
                    found = False
                    for note in reversed(notes):
                        if note.pitch == event.pitch:
                            duration = location - note.location
                            # print " -> duration = %.2f beats" % duration
                            note.duration = duration
                            found = True
                            break
                    if not found:
                        log.warn("*** NOTE-OFF FOUND WITHOUT NOTE-ON ***")

        if quantize is not None:
            for note in notes:
                note.location = round(note.location / quantize) * quantize
                note.duration = round(note.duration / quantize) * quantize

        return notes

    def read(self, filename, quantize = 0.25):
        notes = self.read_note_list(filename, quantize)

        #------------------------------------------------------------------------
        # Construct a sequence which honours chords and relative lengths.
        # First, group all notes by their starting time.
        #------------------------------------------------------------------------
        notes_by_time = {}
        for note in notes:
            log.debug("(%.2f) %d/%d, %s" % (note.location, note.pitch, note.velocity, note.duration))
            location = note.location
            # done in read_note_list
            # if quantize is not None:
            #    location = round(location / quantize) * quantize
            if location in notes_by_time:
                notes_by_time[location].append(note)
            else:
                notes_by_time[location] = [ note ]

        note_dict = {
            "note" : [],
            "amp" :  [],
            "gate" : [],
            "dur" :  []
        }

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
                next_time = time + max([ note.duration for note in notes ])

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

class MidiFileOut:
    """ Write events to a MIDI file.
        Requires the MIDIUtil package:
        https://code.google.com/p/midiutil/ """

    def __init__(self, filename = "score.mid", num_tracks = 16):
        # requires midiutil
        from midiutil.MidiFile import MIDIFile

        self.filename = filename
        self.score = MIDIFile(num_tracks)
        self.time = 0

    def tick(self, tick_length):
        self.time += tick_length

    def note_on(self, note = 60, velocity = 64, channel = 0, duration = 1):
        #------------------------------------------------------------------------
        # avoid rounding errors
        #------------------------------------------------------------------------
        time = round(self.time, 5)
        self.score.addNote(channel, channel, note, time, duration, velocity)

    def note_off(self, note = 60, channel = 0):
        time = round(self.time, 5)
        self.score.addNote(channel, channel, note, time, 0, 0)

    def write(self):
        fd = open(self.filename, 'wb')
        self.score.writeFile(fd)
        fd.close()

class PatternWriterMIDI:
    """ Writes a pattern to a MIDI file.
        Requires the MIDIUtil package:
        https://code.google.com/p/midiutil/ """

    def __init__(self, filename = "score.mid", numtracks = 1):
        from midiutil.MidiFile import MIDIFile

        self.score = MIDIFile(numtracks)
        self.track = 0
        self.channel = 0
        self.volume = 64

    def add_track(self, pattern, track_number = 0, track_name = "track", dur = 1.0):
        time = 0

        # naive approach: assume every duration is 1
        # TODO: accept dicts or PDicts
        try:
            for note in pattern:
                vdur = Pattern.value(dur)
                if note is not None and vdur is not None:
                    self.score.addNote(track_number, self.channel, note, time, vdur, self.volume)
                    time += vdur
                else:
                    time += vdur
        except StopIteration:
            #------------------------------------------------------------------------
            # a StopIteration exception means that an input pattern has been
            # exhausted. catch it and treat the track as completed.
            #------------------------------------------------------------------------
            pass

    def add_timeline(self, timeline):
        #------------------------------------------------------------------------
        # TODO: translate entire timeline into MIDI
        # difficulties: need to handle degree/transpose params
        #               need to handle channels properly, and reset numtracks
        #------------------------------------------------------------------------
        pass

    def write(self, filename = "score.mid"):
        fd = open(filename, 'wb')
        self.score.writeFile(fd)
        fd.close()

