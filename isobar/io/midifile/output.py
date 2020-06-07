from ...pattern import Pattern

import logging

log = logging.getLogger(__name__)

class MidiFileOut:
    """ Write events to a MIDI file.
        Requires the MIDIUtil package:
        https://code.google.com/p/midiutil/ """

    def __init__(self, filename="score.mid", num_tracks=16):
        # requires midiutil
        from midiutil.MidiFile import MIDIFile

        self.filename = filename
        self.score = MIDIFile(num_tracks)
        self.time = 0

    def tick(self, tick_duration):
        self.time += tick_duration

    def note_on(self, note=60, velocity=64, channel=0, duration=1):
        #------------------------------------------------------------------------
        # avoid rounding errors
        #------------------------------------------------------------------------
        time = round(self.time, 5)
        self.score.addNote(channel, channel, note, time, duration, velocity)

    def note_off(self, note=60, channel=0):
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

    def __init__(self, filename="score.mid", numtracks=1):
        from midiutil.MidiFile import MIDIFile

        self.score = MIDIFile(numtracks)
        self.track = 0
        self.channel = 0
        self.volume = 64

    def add_track(self, pattern, track_number=0, track_name="track", dur=1.0):
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

    def write(self, filename="score.mid"):
        fd = open(filename, 'wb')
        self.score.writeFile(fd)
        fd.close()
