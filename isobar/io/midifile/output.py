from ...pattern import Pattern
from ..output import OutputDevice
from mido import Message, MidiFile, MidiTrack

import logging

log = logging.getLogger(__name__)

class MidiFileOutputDevice (OutputDevice):
    """ Write events to a MIDI file.
        """

    def __init__(self, filename):
        self.filename = filename
        self.midifile = MidiFile()
        self.miditrack = MidiTrack()
        self.midifile.tracks.append(self.miditrack)
        self.time = 0
        self.last_event_time = 0

    @property
    def ticks_per_beat(self):
        return self.midifile.ticks_per_beat

    def tick(self):
        self.time += 1.0 / self.ticks_per_beat

    def note_on(self, note=60, velocity=64, channel=0):
        #------------------------------------------------------------------------
        # avoid rounding errors
        #------------------------------------------------------------------------
        dt = self.time - self.last_event_time
        dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
        self.miditrack.append(Message('note_on', note=note, velocity=velocity, channel=channel, time=dt_ticks))
        self.last_event_time = self.time

    def note_off(self, note=60, channel=0):
        dt = self.time - self.last_event_time
        dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
        self.miditrack.append(Message('note_off', note=note, channel=channel, time=dt_ticks))
        self.last_event_time = self.time

    def write(self):
        self.midifile.save(self.filename)

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
