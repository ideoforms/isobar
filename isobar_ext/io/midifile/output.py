from ...pattern import Pattern
from ..output import OutputDevice
from ...constants import DEFAULT_TICKS_PER_BEAT
from ..midi.output import MidiOutputDevice
from mido import Message, MidiFile, MidiTrack


import logging
import re

log = logging.getLogger(__name__)


class MidiFileOutputDevice(OutputDevice):
    """Write events to a MIDI file."""

    def __init__(self, filename, ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
        super().__init__()
        self.filename = filename
        self.midifile = MidiFile(ticks_per_beat=ticks_per_beat)
        self.miditrack = [MidiTrack()]
        self.midifile.tracks.append(self.miditrack[0])
        self.channel_track = [None]
        self.tgt_track_idxs = [None]
        self.time = [0]
        self.last_event_time = [0]

    def get_channel_track(self, channel=None, src_track_idx=None):
        def add_track(chn, tix):
            track = MidiTrack()
            self.miditrack.append(track)
            self.midifile.tracks.append(track)
            self.channel_track.append(chn)
            self.tgt_track_idxs.append(tix)

            self.time.append(0)
            self.last_event_time.append(0)
            return len(self.tgt_track_idxs) - 1

        if src_track_idx is not None and channel is not None:
            if self.tgt_track_idxs == [None] and self.channel_track == [None]:
                self.tgt_track_idxs = [src_track_idx]
                self.channel_track = [channel]
                return 0
            if (channel, src_track_idx) in zip(self.channel_track, self.tgt_track_idxs):
                return list(zip(self.channel_track, self.tgt_track_idxs)).index((channel, src_track_idx))
            if (channel, None) in zip(self.channel_track, self.tgt_track_idxs):
                idx = list(zip(self.channel_track, self.tgt_track_idxs)).index((channel, None))
                self.tgt_track_idxs[idx] = src_track_idx
                return idx
            if (None, src_track_idx) in zip(self.channel_track, self.tgt_track_idxs):
                idx = list(zip(self.channel_track, self.tgt_track_idxs)).index((None, src_track_idx))
                self.channel_track[idx] = channel
                return idx

            return add_track(chn=channel, tix=src_track_idx)

        if src_track_idx is not None:
            if self.tgt_track_idxs == [None] and self.channel_track == [None]:
                self.tgt_track_idxs = [src_track_idx]
                return 0

            if src_track_idx in self.tgt_track_idxs:
                idx = self.tgt_track_idxs.index(src_track_idx)
                return idx

            return add_track(chn=None, tix=src_track_idx)

        if channel is not None:
            if self.tgt_track_idxs == [None] and self.channel_track == [None]:
                self.channel_track = [channel]
                return 0

            if channel in self.channel_track:
                idx = self.channel_track.index(channel)
                return idx

            return add_track(chn=channel, tix=None)
        return 1

    @property
    def ticks_per_beat(self):
        return self.midifile.ticks_per_beat

    def tick(self):
        self.time = list(map(lambda x: x + (1.0 / self.ticks_per_beat), self.time))


    def _msg_deduplication(self):
        new_mid = MidiFile()

        for i, track in enumerate(self.midifile.tracks):
            latest_meta_messages = {}
            new_track = MidiTrack()
            track.reverse()
            for msg in track:
                if msg.time != 0:
                    latest_meta_messages = {}
                if msg.is_meta or (msg.type not in ('note_on', 'note_off')):
                    key = None
                    if msg.type == 'text':
                        key = re.search(r'^.*?:', msg.text)[0]
                    elif hasattr(msg, 'channel'):
                        if msg.type == 'polytouch':
                            key = (msg.type, msg.channel, msg.note)
                        elif msg.type == 'control_change':
                            key = (msg.type, msg.channel, msg.control)
                        else:
                            key = (msg.type, msg.channel)
                    else:
                        key = msg.type

                    if key not in latest_meta_messages:
                        if msg.time == 0:
                            latest_meta_messages[key] = msg
                        new_track.append(msg)

                else:
                    new_track.append(msg)
            new_track.reverse()
            new_mid.tracks.append(new_track)

        self.midifile.tracks = new_mid.tracks
        self.miditrack = new_mid.tracks


    def note_on(self, note=60, velocity=64, channel=0, track_idx=0):
        # ------------------------------------------------------------------------
        # avoid rounding errors
        # ------------------------------------------------------------------------
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                Message('note_on', note=note, velocity=velocity, channel=channel, time=dt_ticks))
            self.last_event_time[track] = self.time[track]

    def note_off(self, note=60, channel=0, track_idx=0):
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(Message('note_off', note=note, channel=channel, time=dt_ticks))
            self.last_event_time[track] = self.time[track]

    def write(self, dedup=True):
        # ------------------------------------------------------------------------
        # When closing the MIDI file, append a dummy `note_off` event to ensure
        # any rests at the end of the file remain intact
        # (cf. https://forum.noteworthycomposer.com/?topic=4708.0)
        # ------------------------------------------------------------------------
        for idx, track in enumerate(self.midifile.tracks):
            dt = self.time[idx] - self.last_event_time[idx]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            track.append(Message('note_off', note=0, channel=0, time=dt_ticks))
        if dedup:
            self._msg_deduplication()
        self.midifile.save(self.filename)

    def control(self, control=0, value=0, channel=0, track_idx=0):
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                Message('control_change', control=int(control), value=int(value), channel=int(channel)))
            self.last_event_time[track] = self.time[track]

    def pitch_bend(self, pitch=0, channel=0, track_idx=0):
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                Message('pitchwheel', pitch=int(pitch), channel=int(channel)))
            self.last_event_time[track] = self.time[track]

    def program_change(self, program=0, channel=0, track_idx=0):
        log.debug("[midi] Program change (channel %d, program_change %d)" % (channel, program))
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                Message('program_change', program=int(program), channel=int(channel)))
            self.last_event_time[track] = self.time[track]

    def aftertouch(self, value=0, channel=0, track_idx=0):
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                msg = Message('aftertouch', value=value, channel=int(channel)))
            self.last_event_time[track] = self.time[track]

    def polytouch(self, value=0, note=0, channel=0, track_idx=0):
        track = self.get_channel_track(channel=channel, src_track_idx=track_idx)
        # track = track_idx  #  tmp change
        if track >= 0:
            dt = self.time[track] - self.last_event_time[track]
            dt_ticks = int(round(dt * self.midifile.ticks_per_beat))
            self.miditrack[track].append(
                msg = Message('polytouch', value=int(value), note=note, channel=int(channel)))
            self.last_event_time[track] = self.time[track]

class PatternWriterMIDI:
    """Writes a pattern to a MIDI file.
    Requires the MIDIUtil package:
    https://code.google.com/p/midiutil/"""

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
                    self.score.addNote(
                        track_number, self.channel, note, time, vdur, self.volume
                    )
                    time += vdur
                else:
                    time += vdur
        except StopIteration:
            # ------------------------------------------------------------------------
            # a StopIteration exception means that an input pattern has been
            # exhausted. catch it and treat the track as completed.
            # ------------------------------------------------------------------------
            pass

    def add_timeline(self, timeline):
        # ------------------------------------------------------------------------
        # TODO: translate entire timeline into MIDI
        # difficulties: need to handle degree/transpose params
        #               need to handle channels properly, and reset numtracks
        # ------------------------------------------------------------------------
        pass

    def write(self, filename="score.mid"):
        fd = open(filename, "wb")
        self.score.writeFile(fd)
        fd.close()


class FileOut(MidiFileOutputDevice, MidiOutputDevice):

    def __init__(self, filename, device_name, send_clock, virtual=False, ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
        MidiFileOutputDevice.__init__(self, filename=filename, ticks_per_beat=ticks_per_beat)
        MidiOutputDevice.__init__(self, device_name=device_name, send_clock=send_clock, virtual=virtual)

    def note_off(self, note=60, channel=0, track_idx=0):
        MidiFileOutputDevice.note_off(self, note=note, channel=channel, track_idx=track_idx)
        MidiOutputDevice.note_off(self, note=note, channel=channel)

    def note_on(self, note=60, velocity=64, channel=0, track_idx=0):
        MidiFileOutputDevice.note_on(self, note=note, velocity=velocity, channel=channel, track_idx=track_idx)
        MidiOutputDevice.note_on(self, note=note, velocity=velocity, channel=channel)

    def program_change(self, program=0, channel=0, track_idx=0):
        MidiFileOutputDevice.program_change(self, program=program, channel=channel, track_idx=track_idx)
        MidiOutputDevice.program_change(self, program=program, channel=channel)

    def control(self, control=0, value=0, channel=0, track_idx=0):
        MidiFileOutputDevice.control(self, control=control, value=value, channel=channel, track_idx=track_idx)
        MidiOutputDevice.control(self, control=control, value=value, channel=channel)

    def pitch_bend(self, pitch=0, channel=0, track_idx=0):
        MidiFileOutputDevice.pitch_bend(self, pitch=pitch, channel=channel, track_idx=track_idx)
        MidiOutputDevice.pitch_bend(self, pitch=pitch, channel=channel)

    def aftertouch(self, control=0, value=0, channel=0, track_idx=0):
        MidiFileOutputDevice.aftertouch(self, value=value, channel=channel,
                                                  track_idx=track_idx)

    def polytouch(self, value=0, note=0, channel=0, track_idx=0):
        MidiFileOutputDevice.polytouch(self, value=value, note=note, channel=channel, track_idx=track_idx)

    def write(self, dedup=True):
        MidiFileOutputDevice.write(self, dedup)