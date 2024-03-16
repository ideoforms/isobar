""" Unit tests for Key """

import os
# import copy
import mido
from typing import Iterable

import isobar_ext as iso
from isobar_ext.io.midifile import MidiFileOutputDevice, MidiFileInputDevice
from isobar_ext.io.midimessages import (
    MidiMetaMessageTempo, MidiMetaMessageKey, MidiMetaMessageTimeSig,
    MidiMetaMessageTrackName, MidiMetaMessageMidiPort, MidiMetaMessageEndTrack, MidiMessageControl,
    MidiMessageProgram, MidiMessagePitch, MidiMessagePoly, MidiMessageAfter
)
import pytest
from tests import dummy_timeline, IN_CI_CD
# from unittest.mock import MagicMock, Mock


# def xmid_meta_message(dummy_tim: iso.Timeline , msg: mido.MetaMessage = None, *args, **kwargs):
#     # return None
#     track_idx = min(kwargs.pop('track_idx', 0), len(dummy_tim.output_device.miditrack) - 1)
#     if not msg:
#         msg = mido.MetaMessage(*args, **kwargs)
#     dummy_tim.output_device.miditrack[track_idx].append(msg)
#
#
# def xset_tempo(tempo):
#     mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)
#
#
# def xtrack_name(name, track_idx=0):
#     mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)

def test_io_midifile_write_rests(dummy_timeline):
    events = {
        iso.EVENT_NOTE: iso.PSequence([60, None, 55, None], 1),
        iso.EVENT_DURATION: iso.PSequence([0.5, 1.5, 1, 1], 1),
        iso.EVENT_GATE: iso.PSequence([2, 0.5, 1, 1], 1),
        iso.EVENT_AMPLITUDE: iso.PSequence([64, 32, 16, 8], 1)
    }

    midifile = MidiFileOutputDevice("output.mid")
    dummy_timeline.output_device = midifile
    dummy_timeline.schedule(events)
    dummy_timeline.run()
    midifile.write()

    d = MidiFileInputDevice("output.mid").read()
    # when reading from a file, the last event is added to match beat lengths considering the time signature
    # total duration is 4 thanks to that.
    for key in events.keys():
        assert isinstance(d[key], iso.PSequence)
        if key == iso.EVENT_NOTE:
            assert list(d[key]) == [e or 0 for e in list(events[key])] + [0]
        elif key == iso.EVENT_DURATION:
            assert pytest.approx(list(d[key]), rel=0.1) == list(events[key]) + [0.002083333333333215]
        elif key == iso.EVENT_GATE:
            assert pytest.approx(list(d[key]), rel=0.3) == list(events[key]) + [1.9958333333333333]
        elif key == iso.EVENT_AMPLITUDE:
            amp = [am if nt else 0 for (am, nt) in zip(events[key].sequence, events[iso.EVENT_NOTE].sequence)] + [0]
            assert list(d[key]) == amp
        else:
            assert list(d[key]) == list(events[key])

    os.unlink("output.mid")

@pytest.mark.skip
def test_cprofile(dummy_timeline, tmp_path):
    # pattern_len(dummy_timeline, dummy_timeline2)
    # import cProfile
    # # cProfile.run('pattern_len(dummy_timeline, dummy_timeline2)')
    # cProfile.runctx('test_io_midifile_write_multi(dummy_timeline, tmp_path)', globals(), locals())
    from pyinstrument import Profiler
    profiler = Profiler()
    profiler.start()
    test_io_midifile_write_multi(dummy_timeline, tmp_path)
    profiler.stop()
    profiler.print()

# @pytest.mark.skip
def test_io_midifile_write_multi(dummy_timeline, tmp_path):
    events_1 = {

        iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52, 55, 57], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1, 1, 1.5], repeats=1)
        , iso.EVENT_CHANNEL: 0
        , iso.EVENT_ACTION_ARGS: {'track_idx': 0}
    }
    events_2 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72, 66], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1, 1], repeats=1)
        , iso.EVENT_CHANNEL: 2
        , iso.EVENT_ACTION_ARGS : {'track_idx': 5}
    }
    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile

    dummy_timeline.schedule(events_1, sel_track_idx=0)
    dummy_timeline.schedule(events_2, sel_track_idx=1)

    dummy_timeline.run()
    assert len(midifile.miditrack) == 2, "2 tracks expected in midifile"
    midifile.write()

    midi_file_in = MidiFileInputDevice(filename)
    d = midi_file_in.read(multi_track_file=True)

    for idx, events in enumerate([events_1, events_2]):
        for key in events.keys():
            if isinstance(d[idx][key], dict):
                assert d[idx][key].get('track_idx') == idx
            else:
                assert isinstance(d[idx][key], iso.PSequence)
                if isinstance(events[key], Iterable):
                    assert list(d[idx][key]) == list(events[key])
                else:
                    assert d[idx][key] == events[key] * len(d[idx][key])


    os.unlink(filename)




def test_io_midifile_write_multi_list(dummy_timeline, tmp_path):
    events_1 = {

        iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52, 55, 57], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1, 1, 1.5], repeats=1)
        , iso.EVENT_CHANNEL: 0
        , iso.EVENT_ACTION_ARGS: {'track_idx': 0}
    }
    events_2 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72, 66], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1, 1], repeats=1)
        , iso.EVENT_CHANNEL: 2
        , iso.EVENT_ACTION_ARGS : {'track_idx': 5}
    }

    # test1 for checking manually prepared list
    event_list = [events_1.copy(), events_2.copy()]
    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dum_tim2 = dummy_timeline
    dummy_timeline.output_device = midifile

    dummy_timeline.schedule(event_list)

    dummy_timeline.run()
    assert len(midifile.miditrack) == 2, "2 tracks expected in midifile"
    midifile.write()

    midi_file_in = MidiFileInputDevice(filename)
    d = midi_file_in.read(multi_track_file=True)


    for idx, events in enumerate(event_list):
        for key in events.keys():
            if isinstance(d[idx][key], dict):
                assert d[idx][key].get('track_idx') == idx
            else:
                assert isinstance(d[idx][key], iso.PSequence)
                if isinstance(events[key], Iterable):
                    assert list(d[idx][key]) == list(events[key])
                else:
                    assert d[idx][key] == events[key] * len(d[idx][key])


    # test1 for checking pattern list read from file
    filename2 = tmp_path/"output2.mid"
    midifile2 = MidiFileOutputDevice(filename2)
    dum_tim2.output_device = midifile2
    d = midi_file_in.read(multi_track_file=True)  # this is needed otherwise sequences are not reset
    dum_tim2.schedule(d)
    dum_tim2.run()

    midifile2.write()

    midi_file_in2 = MidiFileInputDevice(filename2)
    d2 = midi_file_in2.read(multi_track_file=True)

    for idx, events in enumerate(event_list):
        for key in events.keys():
            if isinstance(d2[idx][key], dict):
                assert d2[idx][key].get('track_idx') == idx
            else:
                assert isinstance(d2[idx][key], iso.PSequence)
                if isinstance(events[key], Iterable):
                    assert list(d2[idx][key]) == list(events[key])
                else:
                    assert d2[idx][key] == events[key] * len(d2[idx][key])

    return



@pytest.mark.skipif(IN_CI_CD, reason="Skipped in CI/CD environment")
def test_action_multi(dummy_timeline, tmp_path):
    def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
        # return None
        track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
        if not msg:
            msg = mido.MetaMessage(*args, **kwargs)
        dummy_timeline.output_device.miditrack[track_idx].append(msg)

    def set_tempo(tempo):
        # dummy_timeline.set_tempo(int(tempo))
        # tempo = mido.tempo2bpm(msg.tempo)
        mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)

    def track_name(name, track_idx=0):
        mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)
    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile

    events_1 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1], repeats=1)
        , iso.EVENT_CHANNEL: 0
        # , iso.EVENT_PROGRAM_CHANGE: 0
    }

    events_2 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1], repeats=1)
        , iso.EVENT_CHANNEL: 2
    }

    pgm_1 = {
        iso.EVENT_CHANNEL: 0
        , iso.EVENT_PROGRAM_CHANGE: iso.PSequence([99], repeats=1)
    }

    pgm_2 = {
        iso.EVENT_CHANNEL: 2
        , iso.EVENT_PROGRAM_CHANGE: iso.PSequence([56], repeats=1)
    }

    events_action = {
        iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        , iso.EVENT_ACTION: iso.PSequence(
            sequence=[lambda track_idx=None: (set_tempo(31), set_tempo(35), track_name('blah'), dummy_timeline.track_name('blaxx', 1)),
                      lambda track_idx=None: set_tempo(30),
                      lambda track_idx=None: set_tempo(300), lambda track_idx=None: set_tempo(200)], repeats=1)

    }


    dummy_timeline.schedule(pgm_1, sel_track_idx=0)
    dummy_timeline.schedule(pgm_2, sel_track_idx=1)
    dummy_timeline.schedule(events_action, sel_track_idx=0)
    dummy_timeline.schedule(events_1, sel_track_idx=0)
    dummy_timeline.schedule(events_2, sel_track_idx=1)

    dummy_timeline.run()
    # return
    assert len(midifile.miditrack) == 2, "2 tracks expected in midifile"
    midifile.write()

    midi_file_in = MidiFileInputDevice(filename)
    d = midi_file_in.read(multi_track_file=True)
    # return
    # for idx, events in enumerate([events_1, events_2]):
    for idx, events in enumerate([pgm_1, events_action, pgm_2, events_1, events_2]):
        for key in events.keys():
            if isinstance(d[idx][key], dict):
                assert d[idx][key].get('track_idx') == idx
            else:
                assert isinstance(d[idx][key], iso.PSequence)
                if isinstance(events[key], Iterable):
                    assert list(d[idx][key]) == list(events[key])
                else:
                    assert d[idx][key] == events[key] * len(d[idx][key])


    os.unlink(filename)

def test_action_and_dedup(dummy_timeline, tmp_path):
    def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
        # return None
        track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
        if not msg:
            msg = mido.MetaMessage(*args, **kwargs)
        dummy_timeline.output_device.miditrack[track_idx].append(msg)

    def set_tempo(tempo):
        # dummy_timeline.set_tempo(int(tempo))
        # tempo = mido.tempo2bpm(msg.tempo)
        mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)

    def track_name(name, track_idx=0):
        mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)
    ticks_per_beat = dummy_timeline.ticks_per_beat
    tempo = dummy_timeline.tempo


    events_1_list = [[50, 51, 52, 53],
                     [1, 1, 1, 1]]
    program_nr = 99
    test_track_name = 'blah'
    tempo = [222, 333, 444, 555, 666, 777, 888]
    action_1_list = [
        [lambda track_idx=None: (set_tempo(tempo[0]), set_tempo(tempo[1]), set_tempo(tempo[2]), track_name(test_track_name)),
         lambda track_idx=None: set_tempo(tempo[3]),
         lambda track_idx=None: set_tempo(tempo[4]),
         lambda track_idx=None: (set_tempo(tempo[5]), set_tempo(tempo[6]))],
        [1, 1, 1, 1]
    ]

    baseline_track = mido.MidiTrack([
        mido.Message('program_change', channel=0, program=program_nr, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[0])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[1])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[2])), time=0),
        mido.MetaMessage('track_name', name=test_track_name, time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][0], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][0], velocity=64, time=events_1_list[1][0]*ticks_per_beat),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[3])), time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][1], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][1], velocity=64, time=events_1_list[1][1]*ticks_per_beat),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[4])), time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][2], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][2], velocity=64, time=events_1_list[1][2]*ticks_per_beat),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[5])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[6])), time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][3], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][3], velocity=64, time=events_1_list[1][3]*ticks_per_beat)])

    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile



    events_list = events_1_list
    events_1 = {
        #     iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52], repeats=1)
        # , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1], repeats=1)
        iso.EVENT_NOTE: iso.PSequence(sequence=events_list[0], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=events_list[1], repeats=1)
        , iso.EVENT_CHANNEL: 0
        # , iso.EVENT_PROGRAM_CHANGE: 0
    }

    pgm_1 = {
        iso.EVENT_CHANNEL: 0
        , iso.EVENT_PROGRAM_CHANGE: iso.PSequence([program_nr], repeats=1)
    }


    actions_list = action_1_list
    events_action = {
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        iso.EVENT_DURATION: iso.PSequence(sequence=actions_list[1], repeats=1)
        , iso.EVENT_ACTION: iso.PSequence(
            # sequence=[lambda track_idx=None: (set_tempo(222), set_tempo(111), track_name('blah'), dummy_timeline.track_name('blaxx', 1)),
            #           lambda track_idx=None: set_tempo(444),
            #           lambda track_idx=None: set_tempo(555), lambda track_idx=None: set_tempo(666)], repeats=1)
            sequence=actions_list[0], repeats=1)

    }



    dummy_timeline.schedule(pgm_1, sel_track_idx=0)
    dummy_timeline.schedule(events_action, sel_track_idx=0)
    dummy_timeline.schedule(events_1, sel_track_idx=0)

    dummy_timeline.run()
    # return
    assert len(midifile.miditrack) == 1, "1 track expected in midifile"
    assert baseline_track == midifile.miditrack[0], "Baseline and generated track not equal"

    midifile.write()
    baseline_track.remove(
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[0])), time=0))
    baseline_track.remove(
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[1])), time=0))
    baseline_track.remove(
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[5])), time=0))
    #  extend with end of track
    baseline_track.append(mido.Message('note_off', channel=0, note=0, velocity=64, time=0))
    assert baseline_track == midifile.miditrack[0], "Deduplicated: Baseline and generated track not equal"

    return

def test_action_off_beat(dummy_timeline, tmp_path):
    def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
        # return None
        track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
        if not msg:
            msg = mido.MetaMessage(*args, **kwargs)
        dummy_timeline.output_device.miditrack[track_idx].append(msg)

    def set_tempo(tempo):
        # dummy_timeline.set_tempo(int(tempo))
        # tempo = mido.tempo2bpm(msg.tempo)
        mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)

    def track_name(name, track_idx=0):
        mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)
    ticks_per_beat = dummy_timeline.ticks_per_beat
    tempo = dummy_timeline.tempo


    events_1_list = [[50, 51, 52, 53],
                     [1, 1, 1, 1]]
    program_nr = 99
    test_track_name = 'blah'
    def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
        # return None
        track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
        if not msg:
            msg = mido.MetaMessage(*args, **kwargs)
        dummy_timeline.output_device.miditrack[track_idx].append(msg)

    def set_tempo(tempo):
        # dummy_timeline.set_tempo(int(tempo))
        # tempo = mido.tempo2bpm(msg.tempo)
        mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)

    def track_name(name, track_idx=0):
        mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)
    ticks_per_beat = dummy_timeline.ticks_per_beat
    tempo = dummy_timeline.tempo


    events_1_list = [[50, 51, 52, 53],
                     [1, 1, 1, 1]]
    program_nr = 99
    test_track_name = 'blah'
    tempo = [222, 333, 444, 555, 666, 777, 888]
    action_1_list = [
        [lambda track_idx=None: (set_tempo(tempo[0]), set_tempo(tempo[1]), set_tempo(tempo[2]), track_name(test_track_name)),
         lambda track_idx=None: set_tempo(tempo[3]),
         lambda track_idx=None: set_tempo(tempo[4]),
         lambda track_idx=None: (set_tempo(tempo[5]), set_tempo(tempo[6]))],
        [1.22, 1.3, 1.33, 1.41]
        # [1.22, 2.52, 3.85, 5.26]
    ]

    baseline_track = mido.MidiTrack([
        mido.Message('program_change', channel=0, program=program_nr, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[0])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[1])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[2])), time=0),
        mido.MetaMessage('track_name', name=test_track_name, time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][0], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][0], velocity=64, time=events_1_list[1][0]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][1], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[3])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][1], velocity=64, time=events_1_list[1][1]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][2], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[4])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][2], velocity=64, time=events_1_list[1][2]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][3], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[5])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[6])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][3], velocity=64, time=events_1_list[1][3]*ticks_per_beat)])

    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile



    events_list = events_1_list
    events_1 = {
        #     iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52], repeats=1)
        # , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1], repeats=1)
        iso.EVENT_NOTE: iso.PSequence(sequence=events_list[0], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=events_list[1], repeats=1)
        , iso.EVENT_CHANNEL: 0
        # , iso.EVENT_PROGRAM_CHANGE: 0
    }

    pgm_1 = {
        iso.EVENT_CHANNEL: 0
        , iso.EVENT_PROGRAM_CHANGE: iso.PSequence([program_nr], repeats=1)
    }


    actions_list = action_1_list
    events_action = {
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        iso.EVENT_DURATION: iso.PSequence(sequence=actions_list[1], repeats=1)
        , iso.EVENT_ACTION: iso.PSequence(
            # sequence=[lambda track_idx=None: (set_tempo(222), set_tempo(111), track_name('blah'), dummy_timeline.track_name('blaxx', 1)),
            #           lambda track_idx=None: set_tempo(444),
            #           lambda track_idx=None: set_tempo(555), lambda track_idx=None: set_tempo(666)], repeats=1)
            sequence=actions_list[0], repeats=1)

    }


    dummy_timeline.schedule(pgm_1, sel_track_idx=0)
    dummy_timeline.schedule(events_action, sel_track_idx=0)
    dummy_timeline.schedule(events_1, sel_track_idx=0)


    dummy_timeline.run()
    # return
    assert len(midifile.miditrack) == 1, "1 track expected in midifile"
    assert baseline_track == midifile.miditrack[0], "Baseline and generated track not equal"
    return
    tempo = [222, 333, 444, 555, 666, 777, 888]
    action_1_list = [
        [lambda track_idx=None: (set_tempo(tempo[0]), set_tempo(tempo[1]), set_tempo(tempo[2]), track_name(test_track_name)),
         lambda track_idx=None: set_tempo(tempo[3]),
         lambda track_idx=None: set_tempo(tempo[4]),
         lambda track_idx=None: (set_tempo(tempo[5]), set_tempo(tempo[6]))],
        [1.22, 1.3, 1.33, 1.41]
        # [1.22, 2.52, 3.85, 5.26]
    ]

    baseline_track = mido.MidiTrack([
        mido.Message('program_change', channel=0, program=program_nr, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[0])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[1])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[2])), time=0),
        mido.MetaMessage('track_name', name=test_track_name, time=0),
        mido.Message('note_on', channel=0, note=events_1_list[0][0], velocity=64, time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][0], velocity=64, time=events_1_list[1][0]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][1], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[3])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][1], velocity=64, time=events_1_list[1][1]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][2], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[4])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][2], velocity=64, time=events_1_list[1][2]*ticks_per_beat),
        mido.Message('note_on', channel=0, note=events_1_list[0][3], velocity=64, time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[5])), time=0),
        mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[6])), time=0),
        mido.Message('note_off', channel=0, note=events_1_list[0][3], velocity=64, time=events_1_list[1][3]*ticks_per_beat)])

    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile



    events_list = events_1_list
    events_1 = {
        #     iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52], repeats=1)
        # , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1], repeats=1)
        iso.EVENT_NOTE: iso.PSequence(sequence=events_list[0], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=events_list[1], repeats=1)
        , iso.EVENT_CHANNEL: 0
        # , iso.EVENT_PROGRAM_CHANGE: 0
    }

    pgm_1 = {
        iso.EVENT_CHANNEL: 0
        , iso.EVENT_PROGRAM_CHANGE: iso.PSequence([program_nr], repeats=1)
    }


    actions_list = action_1_list
    events_action = {
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        # iso.EVENT_DURATION: iso.PSequence(sequence=[1.22, 1.3, 1.33, 1.41], repeats=1)
        iso.EVENT_DURATION: iso.PSequence(sequence=actions_list[1], repeats=1)
        , iso.EVENT_ACTION: iso.PSequence(
            # sequence=[lambda track_idx=None: (set_tempo(222), set_tempo(111), track_name('blah'), dummy_timeline.track_name('blaxx', 1)),
            #           lambda track_idx=None: set_tempo(444),
            #           lambda track_idx=None: set_tempo(555), lambda track_idx=None: set_tempo(666)], repeats=1)
            sequence=actions_list[0], repeats=1)

    }


    dummy_timeline.schedule(pgm_1, sel_track_idx=0)
    dummy_timeline.schedule(events_action, sel_track_idx=0)
    dummy_timeline.schedule(events_1, sel_track_idx=0)


    dummy_timeline.run()
    # return
    assert len(midifile.miditrack) == 1, "1 track expected in midifile"
    assert baseline_track == midifile.miditrack[0], "Baseline and generated track not equal"
    return



@pytest.mark.skip
def test_note_repeat(dummy_timeline, tmp_path):
    def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
        # return None
        track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
        if not msg:
            msg = mido.MetaMessage(*args, **kwargs)
        dummy_timeline.output_device.miditrack[track_idx].append(msg)

    def set_tempo(tempo):
        # dummy_timeline.set_tempo(int(tempo))
        # tempo = mido.tempo2bpm(msg.tempo)
        mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)

    def track_name(name, track_idx=0):
        mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)
    ticks_per_beat = dummy_timeline.ticks_per_beat
    tempo = dummy_timeline.tempo


    events_1_list = [[50, 51, 52, 53],
                     [1, 0.5, 0.5, .25]]


    # baseline_track = mido.MidiTrack([
    #     mido.Message('program_change', channel=0, program=program_nr, time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[0])), time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[1])), time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[2])), time=0),
    #     mido.MetaMessage('track_name', name=test_track_name, time=0),
    #     mido.Message('note_on', channel=0, note=events_1_list[0][0], velocity=64, time=0),
    #     mido.Message('note_off', channel=0, note=events_1_list[0][0], velocity=64, time=events_1_list[1][0]*ticks_per_beat),
    #     mido.Message('note_on', channel=0, note=events_1_list[0][1], velocity=64, time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[3])), time=0),
    #     mido.Message('note_off', channel=0, note=events_1_list[0][1], velocity=64, time=events_1_list[1][1]*ticks_per_beat),
    #     mido.Message('note_on', channel=0, note=events_1_list[0][2], velocity=64, time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[4])), time=0),
    #     mido.Message('note_off', channel=0, note=events_1_list[0][2], velocity=64, time=events_1_list[1][2]*ticks_per_beat),
    #     mido.Message('note_on', channel=0, note=events_1_list[0][3], velocity=64, time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[5])), time=0),
    #     mido.MetaMessage('set_tempo', tempo=int(mido.tempo2bpm(tempo[6])), time=0),
    #     mido.Message('note_off', channel=0, note=events_1_list[0][3], velocity=64, time=events_1_list[1][3]*ticks_per_beat)])

    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile


    rep = 2
    events_list = events_1_list
    events_1 = {
        #     iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52], repeats=1)
        # , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1], repeats=1)
        iso.EVENT_NOTE: iso.PSequence(sequence=events_list[0], repeats=rep)
        , iso.EVENT_DURATION: iso.PSequence(sequence=events_list[1], repeats=rep)
        , iso.EVENT_CHANNEL: 0
        # , iso.EVENT_PROGRAM_CHANGE: 0
    }



    dummy_timeline.schedule(events_1, sel_track_idx=0)


    dummy_timeline.run()
    # return
    assert len(midifile.miditrack) == 1, "1 track expected in midifile"
    assert baseline_track == midifile.miditrack[0], "Baseline and generated track not equal"
    return

@pytest.mark.skip
def test_deduplication():
    pass


@pytest.mark.skip
def test_action_notes_pgm():
    pass


@pytest.mark.skip
def test_instantialization_of_mid_obj():
    pass

