""" Unit tests for Key """

import os
# import copy
from typing import Iterable

import isobar_ext as iso
from isobar_ext.io.midifile import MidiFileOutputDevice, MidiFileInputDevice
from isobar_ext.io.midimessages import (
    MidiMetaMessageTempo, MidiMetaMessageKey, MidiMetaMessageTimeSig,
    MidiMetaMessageTrackName, MidiMetaMessageMidiPort, MidiMetaMessageEndTrack, MidiMessageControl,
    MidiMessageProgram, MidiMessagePitch, MidiMessagePoly, MidiMessageAfter
)
import pytest
from tests import dummy_timeline
# from unittest.mock import MagicMock, Mock


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


def test_io_midifile_write_multi(dummy_timeline, tmp_path):
    events1 = {

        iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52, 55, 57], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1, 1, 1.5], repeats=1)
        , iso.EVENT_CHANNEL: 0
        , iso.EVENT_ACTION_ARGS: {'track_idx': 0}
    }
    events2 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72, 66], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1, 1], repeats=1)
        , iso.EVENT_CHANNEL: 2
        , iso.EVENT_ACTION_ARGS : {'track_idx': 5}
    }
    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dummy_timeline.output_device = midifile

    dummy_timeline.schedule(events1, sel_track_idx=0)
    dummy_timeline.schedule(events2, sel_track_idx=1)

    dummy_timeline.run()
    midifile.write()

    midi_file_in = MidiFileInputDevice(filename)
    d = midi_file_in.read(multi_track_file=True)

    for idx, events in enumerate([events1, events2]):
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
    events1 = {

        iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52, 55, 57], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1, 1, 1.5], repeats=1)
        , iso.EVENT_CHANNEL: 0
        , iso.EVENT_ACTION_ARGS: {'track_idx': 0}
    }
    events2 = {
        iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72, 66], repeats=1)
        , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1, 1], repeats=1)
        , iso.EVENT_CHANNEL: 2
        , iso.EVENT_ACTION_ARGS : {'track_idx': 5}
    }

    # test1 for checking manually prepared list
    event_list = [events1.copy(), events2.copy()]
    filename = tmp_path/"output.mid"
    midifile = MidiFileOutputDevice(filename)
    dum_tim2 = dummy_timeline
    dummy_timeline.output_device = midifile

    dummy_timeline.schedule(event_list)

    dummy_timeline.run()
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

