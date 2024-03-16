import logging
from collections.abc import Iterable
from functools import partial
import mido

from ..midimessages import (MidiMessageControl, MidiMessageProgram, MidiMessagePitch, MidiMessagePoly, MidiMessageAfter,
                            MidiMetaMessageTempo, MidiMetaMessageEndTrack, MidiMetaMessageTrackName, 
                            MidiMetaMessageMidiPort, MidiMetaMessageKey, MidiMetaMessageTimeSig)
from ..midinote import MidiNote
from ...constants import (EVENT_NOTE, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_GATE, EVENT_ACTION, EVENT_ACTION_ARGS,
                          EVENT_TIME, EVENT_CHANNEL)
from ...pattern import PSequence

log = logging.getLogger(__name__)


class MidiFileInputDevice:
    """Read events from a MIDI file.
    Requires mido."""

    def __init__(self, filename):
        self.filename = filename
        self.midi_reader = mido.MidiFile(self.filename)

    # def set_tempo_callback(self, tempo):
    def set_tempo_callback(self, *args, **kwargs):
        pass

    def midi_message_obj(self, timeline_inner, objects=None, track_idx=0):

        if not isinstance(objects, Iterable):
            objects = [objects]
        text = [(type(o), o.__dict__) for o in objects]
        midi_track0 = timeline_inner.output_device.miditrack[0]

        for obj in objects:
            if isinstance(obj, MidiMetaMessageTempo):
                timeline_inner.set_tempo(int(mido.tempo2bpm(obj.tempo)))
                self.set_tempo_callback(int(mido.tempo2bpm(obj.tempo)))
                msg = mido.MetaMessage('text', text=f"tempo:{int(mido.tempo2bpm(obj.tempo))}")
                midi_track0.append(msg)
            elif isinstance(obj, MidiMessageControl):
                timeline_inner.output_device.control(control=obj.cc, value=obj.value, channel=obj.channel,
                                                     track_idx=track_idx)
            elif isinstance(obj, MidiMessageProgram):
                timeline_inner.output_device.program_change(program=obj.program, channel=obj.channel,
                                                            track_idx=track_idx)
            elif isinstance(obj, MidiMessagePitch):
                timeline_inner.output_device.pitch_bend(self, pitch=obj.pitch, channel=obj.channel,
                                                        track_idx=track_idx)
            elif isinstance(obj, MidiMessageAfter):
                timeline_inner.output_device.aftertouch(self, value=obj.value,
                                                        channel=obj.channel, track_idx=track_idx)
            elif isinstance(obj, MidiMessagePoly):
                timeline_inner.output_device.polytouch(self, note=obj.note, value=obj.value,
                                                       channel=obj.channel, track_idx=track_idx)

            if midi_track0 is not None and hasattr(obj, 'to_meta_message'):
                channel_param = obj.channel if hasattr(obj, 'channel') else None
                new_track_idx = timeline_inner.output_device.get_channel_track(channel=channel_param,
                                                                               src_track_idx=track_idx)
                timeline_inner.output_device.miditrack[new_track_idx].append(obj.to_meta_message())

    def read(self, quantize=None, ms_to_filter=None, multi_track_file=False):
        def create_lam_function(tgt_dict, messages_inner, track_idx_inner=0):
            lam_function = partial(self.midi_message_obj, objects=messages_inner, track_idx=track_idx_inner)
            tgt_dict[EVENT_ACTION].append(lam_function)
            if isinstance(messages_inner, Iterable):
                msg_loc = messages_inner[0].location
            else:
                msg_loc = messages_inner.location
            tgt_dict[EVENT_TIME].append(msg_loc)

        if ms_to_filter is None:
            ms_to_filter = ['end_of_track']

        note_tracks = self.midi_reader.tracks
        log.info(
            "Loading MIDI data from %s, ticks per beat = %d"
            % (self.filename, self.midi_reader.ticks_per_beat)
        )
        any_track_with_notes = list(
            filter(lambda track: any(message.type == "note_on" for message in track),
                self.midi_reader.tracks)
        )
        if not any_track_with_notes and not note_tracks:
            raise ValueError("Could not find any tracks with note data")

        tracks_note_dict = []
        channel_calc = 0
        for track_idx, track in enumerate(note_tracks):
            # track_idx = note_tracks.index(track)
            notes = []
            offset = 0
            offset_int = 0
            for event in track:
                if event.type == 'note_on' and (event.velocity > 0 or event.note == 0):
                    # ------------------------------------------------------------------------
                    # Found a note_on event.
                    # ------------------------------------------------------------------------

                    # ------------------------------------------------------------------------
                    # Sanitisation (some midifiles seem to give invalid input).
                    # ------------------------------------------------------------------------
                    if event.velocity > 127:
                        event.velocity = 127

                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    note_int = MidiNote( pitch=event.note, velocity=event.velocity, location=offset, channel=event.channel)
                    notes.append(note_int)
                # elif event.type == 'note_off' or (event.type == 'note_on' and event.velocity == 0):
                elif event.type == 'note_off' or (event.type == 'note_on'):
                    # ------------------------------------------------------------------------
                    # Found a note_off event.
                    # ------------------------------------------------------------------------
                    # filter note_off fake marker
                    fake_note_off = {'type': 'note_off', 'note': 0, 'velocity': 64, 'channel': 0}
                    if {k: v for (k, v) in event.__dict__.items() if k in fake_note_off} == fake_note_off:
                        continue
                    # if event.__dict__ == {'type': 'note_off', 'time': 0, 'note': 0, 'velocity': 64, 'channel': 0}:
                    #     continue
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    for note_int in reversed(notes):
                        if not isinstance(note_int, MidiNote):
                            continue
                        if note_int.pitch == event.note and note_int.duration is None:
                            note_int.duration = offset - note_int.location
                            break
                elif event.type == 'program_change':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    pgm_chg = MidiMessageProgram(channel=event.channel, program=event.program, location=offset,
                                                 track_idx=track_idx)
                    notes.append(pgm_chg)
                elif event.type == 'control_change':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    ctrl_chg = MidiMessageControl(channel=event.channel, cc=event.control, value=event.value,
                                                  location=offset, time=event.time, track_idx=track_idx)
                    notes.append(ctrl_chg)
                elif event.type == 'polytouch':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    poly_touch = MidiMessagePoly(channel=event.channel, note=event.note, value=event.value,
                                                 location=offset, time=event.time, track_idx=track_idx)
                    notes.append(poly_touch)
                elif event.type == 'aftertouch':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    after_touch = MidiMessageAfter(channel=event.channel, value=event.value, location=offset,
                                                   time=event.time, track_idx=track_idx)
                    notes.append(after_touch)
                elif event.type == 'pitchwheel':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    pitch_wheel = MidiMessagePitch(channel=event.channel, pitch=event.pitch, location=offset,
                                                   time=event.time, track_idx=track_idx)
                    notes.append(pitch_wheel)

                elif event.type == 'end_of_track':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    end_of_track = MidiMetaMessageEndTrack(location=offset,
                                                           time=event.time, track_idx=track_idx)
                    #  disable this temporarily - this is rather not needed, but breaks len calc
                    if 'end_of_track' not in ms_to_filter:
                        notes.append(end_of_track)
                elif event.type == 'midi_port':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    midi_port = MidiMetaMessageMidiPort(port=event.port, location=offset,
                                                        time=event.time, track_idx=track_idx)
                    notes.append(midi_port)
                elif event.type == 'key_signature':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    key_sig = MidiMetaMessageKey(key=event.key, location=offset,
                                                 time=event.time, track_idx=track_idx)
                    notes.append(key_sig)
                elif event.type == 'time_signature':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    time_sig = MidiMetaMessageTimeSig(numerator=event.numerator, denominator=event.denominator,
                                                      clocks_per_click=event.clocks_per_click,
                                                      notated_32nd_notes_per_beat=event.notated_32nd_notes_per_beat,
                                                      location=offset, time=event.time, track_idx=track_idx)
                    notes.append(time_sig)
                elif event.type == 'track_name':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    track_name = MidiMetaMessageTrackName(name=event.name, location=offset, time=event.time,
                                                          track_idx=track_idx)
                    notes.append(track_name)
                elif event.type == 'set_tempo':
                    offset_int += event.time
                    offset = offset_int / self.midi_reader.ticks_per_beat
                    tempo = MidiMetaMessageTempo(tempo=event.tempo, location=offset, time=event.time,
                                                 track_idx=track_idx)
                    notes.append(tempo)

            # ------------------------------------------------------------------------
            # Quantize
            # ------------------------------------------------------------------------
            if quantize:
                for note_int in notes:
                    note_int.location = round(note_int.location / quantize) * quantize
                    if hasattr(note_int, 'duration'):
                        note_int.duration = round(note_int.duration / quantize) * quantize

            # ------------------------------------------------------------------------
            # Construct a sequence which honours chords and relative lengths.
            # First, group all notes by their starting time.
            # ------------------------------------------------------------------------
            notes_by_time = {}
            action_by_time = {}
            non_meta_by_time = {}
            for note_int in notes:
                if isinstance(note_int, MidiNote):
                    if not note_int.duration:
                        note_int.duration = 1
                    log.debug(" - MIDI event (t = %.2f): Note %d, velocity %d, duration %.3f" %
                              (note_int.location, note_int.pitch, note_int.velocity, note_int.duration))
                location = note_int.location
                if isinstance(note_int, MidiNote):
                    if location in notes_by_time:
                        notes_by_time[location].append(note_int)
                    else:
                        notes_by_time[location] = [note_int]
                elif getattr(note_int, 'is_meta', False):
                    if location in action_by_time:
                        action_by_time[location].append(note_int)
                    else:
                        action_by_time[location] = [note_int]
                else:
                    if location in non_meta_by_time:
                        non_meta_by_time[location].append(note_int)
                    else:
                        non_meta_by_time[location] = [note_int]

            note_dict = {
                EVENT_NOTE: [],
                EVENT_AMPLITUDE: [],
                EVENT_GATE: [],
                EVENT_DURATION: [],
                EVENT_CHANNEL: []
            }
            action_dict = {
                EVENT_ACTION: [],
                EVENT_TIME: [],
                EVENT_DURATION: []
            }

            non_meta_dict = {
                EVENT_ACTION: [],
                EVENT_TIME: [],
                EVENT_DURATION: []
            }
            # ------------------------------------------------------------------------
            # Next, iterate through groups of notes chronologically, figuring out
            # appropriate parameters for duration (eg, inter-note distance) and
            # gate (eg, proportion of distance note extends across).
            # ------------------------------------------------------------------------
            non_meta_times = sorted(non_meta_by_time.keys())
            for i, t in enumerate(non_meta_times):
                t = non_meta_times[i]
                notes = non_meta_by_time[t]
                if i < len(non_meta_times) - 1:
                    next_time = non_meta_times[i + 1]
                else:
                    next_time = t + max(
                        [getattr(nt, 'duration') for nt in notes if hasattr(nt, 'duration')] or [1.0])

                # time_until_next_note = next_time - t
                if len(notes) > 1:
                    messages = tuple(nt for nt in notes)
                    create_lam_function(non_meta_dict, messages, track_idx)
                else:
                    create_lam_function(non_meta_dict, notes[0], track_idx)

            action_times = sorted(action_by_time.keys())
            for i, t in enumerate(action_times):
                t = action_times[i]
                notes = action_by_time[t]
                if i < len(action_times) - 1:
                    next_time = action_times[i + 1]
                else:
                    next_time = t + max([nt.duration for nt in notes if hasattr(nt, 'duration')] or [1.0])

                time_until_next_note = next_time - t
                if len(notes) > 1:
                    messages = tuple(nt for nt in notes)
                    create_lam_function(action_dict, messages, track_idx)
                else:
                    create_lam_function(action_dict, notes[0], track_idx)

            times = sorted(notes_by_time.keys())

            time_until_next_note = True  # this
            for i, t in enumerate(times):
                t = times[i]
                notes = notes_by_time[t]

                # ------------------------------------------------------------------------
                # Our duration is always determined by the time of the next note event.
                # If a next note does not exist, this is the last note of the sequence;
                # use the maximal length of note currently playing (assuming a chord)
                # ------------------------------------------------------------------------
                if time_until_next_note:
                    if len(notes) > 1:
                        messages = tuple(nt for nt in notes if not isinstance(nt, MidiNote))
                        note_tuple = tuple(
                            nt.pitch for nt in notes if isinstance(nt, MidiNote))
                        if len(note_tuple):
                            if i < len(times) - 1:
                                next_time = times[i + 1]
                            else:
                                next_time = t + max(
                                    [nt.duration for nt in notes if hasattr(nt, 'duration')] or [1.0])

                            time_until_next_note = next_time - t
                            note_dict[EVENT_DURATION].append(time_until_next_note)
                            note_dict[EVENT_NOTE].append(note_tuple)
                            note_dict[EVENT_AMPLITUDE].append(
                                tuple(nt.velocity for nt in notes if isinstance(nt, MidiNote)))
                            note_dict[EVENT_GATE].append(
                                tuple(
                                    nt.duration / time_until_next_note for nt in notes if isinstance(nt, MidiNote)))
                            note_dict[EVENT_CHANNEL].append(tuple(
                                int(nt.channel) for nt in notes if isinstance(nt, MidiNote)))
                    else:

                        note_int = notes[0]
                        if isinstance(note_int, MidiNote):
                            if i < len(times) - 1:
                                next_time = times[i + 1]
                            else:
                                next_time = t + max(
                                    [nt.duration for nt in notes if
                                     hasattr(nt, 'duration') and isinstance(nt, MidiNote)] or [1.0])

                            time_until_next_note = next_time - t
                            note_dict[EVENT_DURATION].append(time_until_next_note)
                            note_dict[EVENT_NOTE].append(note_int.pitch)
                            note_dict[EVENT_AMPLITUDE].append(note_int.velocity)
                            note_dict[EVENT_GATE].append(note_int.duration / time_until_next_note)
                            note_dict[EVENT_CHANNEL].append(note_int.channel)

            for k, v in note_dict.items():
                note_dict[k] = PSequence(v, repeats=1)

            #  recalculate EVENT_TIME -> EVENT_DURATION
            time_list = action_dict.pop(EVENT_TIME, None)
            if time_list:
                action_dict[EVENT_DURATION] = [dur - time_list[i] for (i, dur) in enumerate(time_list[1:])] + [1.0]

            for k, v in action_dict.copy().items():
                if len(v) != 0:
                    action_dict[k] = PSequence(v, repeats=1)
                else:
                    action_dict.pop(k, None)

            #  recalculate EVENT_TIME -> EVENT_DURATION
            time_list = non_meta_dict.pop(EVENT_TIME, None)
            if time_list:
                non_meta_dict[EVENT_DURATION] = [dur - time_list[i] for (i, dur) in enumerate(time_list[1:])] + [
                    1.0]

            for k, v in non_meta_dict.copy().items():
                if len(v) != 0:
                    non_meta_dict[k] = PSequence(v, repeats=1)
                else:
                    non_meta_dict.pop(k, None)

                # channel_calc += 1

            if bool(non_meta_dict):
                non_meta_dict[EVENT_ACTION_ARGS] = {"track_idx": track_idx}
                tracks_note_dict.append(non_meta_dict)

            if bool(action_dict):
                action_dict[EVENT_ACTION_ARGS] = {"track_idx": track_idx}
                tracks_note_dict.append(action_dict)

            if bool(note_dict):
                note_dict[EVENT_ACTION_ARGS] = {"track_idx": track_idx}
                tracks_note_dict.append(note_dict)

        patterns_from_file_duration = max(
            [sum(pat[EVENT_DURATION].sequence) for pat in tracks_note_dict if
             pat.get(EVENT_DURATION, None)])
        time_signature = next(
            ({'numerator': x.get('numerator'), 'denominator': x.get('denominator')} for x in tracks_note_dict if
             hasattr(x, 'numerator') and hasattr(x, 'denominator')), {'numerator': 4, 'denominator': 4})
        factor = time_signature['numerator'] * 4 / time_signature['denominator']

        dur = patterns_from_file_duration
        dur = dur / factor
        if dur > int(dur):
            dur = int(dur) + 1
        total_duration = dur * factor
        for pat in tracks_note_dict:
            if not (pat.get(EVENT_DURATION, None) and pat.get(EVENT_NOTE, None)):
                continue
            diff_duration = total_duration - sum(pat[EVENT_DURATION].sequence)
            if diff_duration:
                pat[EVENT_DURATION].sequence.append(diff_duration)
                pat[EVENT_NOTE].sequence.append(0)
                if pat.get(EVENT_AMPLITUDE, None):
                    pat[EVENT_AMPLITUDE].sequence.append(0)
                if pat.get(EVENT_GATE, None):
                    pat[EVENT_GATE].sequence.append(pat[EVENT_GATE].sequence[0])
                if pat.get(EVENT_CHANNEL, None):
                    pat[EVENT_CHANNEL].sequence.append(pat[EVENT_CHANNEL].sequence[0])

        if not multi_track_file:
            track = next(t for t in tracks_note_dict if t.get(EVENT_NOTE, None))
            if EVENT_ACTION_ARGS in  track:
                track[EVENT_ACTION_ARGS].pop('track_idx', None)
                if not bool(track[EVENT_ACTION_ARGS]):
                    track.pop(EVENT_ACTION_ARGS, None)

            return track

        return sorted(tracks_note_dict, key=lambda t: 0 if t.get(EVENT_ACTION, None) else 1)

