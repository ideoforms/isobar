import platform
from pathlib import Path

import pytest

from isobar_ext import FileOut, MidiFileOutputDevice


def test_get_channel_track():
    test_midi_out_device = MidiFileOutputDevice(filename='test_output_file')
    test_midi_out_device.get_channel_track(channel=2, src_track_idx=None)
    assert test_midi_out_device.channel_track == [2]
    assert test_midi_out_device.tgt_track_idxs == [None]

    test_midi_out_device = MidiFileOutputDevice(filename='test_output_file')
    test_midi_out_device.get_channel_track(channel=None, src_track_idx=1)
    assert test_midi_out_device.channel_track == [None]
    assert test_midi_out_device.tgt_track_idxs == [1]

    test_midi_out_device = MidiFileOutputDevice(filename='test_output_file')
    test_midi_out_device.get_channel_track(channel=None, src_track_idx=None)
    assert test_midi_out_device.channel_track == [None]
    assert test_midi_out_device.tgt_track_idxs == [None]

    # test_midi_out_device = MidiFileManyTracksOutputDevice(filename='test_output_file')
    test_midi_out_device.get_channel_track(channel=2, src_track_idx=1)
    assert test_midi_out_device.channel_track == [2]
    assert test_midi_out_device.tgt_track_idxs == [1]

    test_midi_out_device.get_channel_track(channel=None, src_track_idx=2)
    assert test_midi_out_device.channel_track == [2, None]
    assert test_midi_out_device.tgt_track_idxs == [1, 2]

    test_midi_out_device.get_channel_track(channel=3, src_track_idx=2)
    assert test_midi_out_device.channel_track == [2, 3]
    assert test_midi_out_device.tgt_track_idxs == [1, 2]

    test_midi_out_device.get_channel_track(channel=4, src_track_idx=2)
    assert test_midi_out_device.channel_track == [2, 3, 4]
    assert test_midi_out_device.tgt_track_idxs == [1, 2, 2]

    test_midi_out_device.get_channel_track(channel=4, src_track_idx=None)
    assert test_midi_out_device.channel_track == [2, 3, 4]
    assert test_midi_out_device.tgt_track_idxs == [1, 2, 2]

    test_midi_out_device.get_channel_track(channel=5, src_track_idx=None)
    assert test_midi_out_device.channel_track == [2, 3, 4, 5]
    assert test_midi_out_device.tgt_track_idxs == [1, 2, 2, None]

    test_midi_out_device.get_channel_track(channel=5, src_track_idx=1)
    assert test_midi_out_device.channel_track == [2, 3, 4, 5]
    assert test_midi_out_device.tgt_track_idxs == [1, 2, 2, 1]

    test_midi_out_device.get_channel_track(channel=5, src_track_idx=2)
    assert test_midi_out_device.channel_track == [2, 3, 4, 5, 5]
    assert test_midi_out_device.tgt_track_idxs == [1, 2, 2, 1, 2]

# from isobar_ext import *
# import mido
# from tracker.app.isobar_fixes import *
# from tracker.app.midi_dev import *

@pytest.mark.skipif(platform.system() == "Linux", reason="Test not supported on Linux")
def test_wrk_midi_out():
    """
    This test check fix for FileOut, which has broken because trying to open midi output device 2 times.
    """
    device_name = 'Microsoft GS Wavetable Synth 0'
    filename = (Path(__file__).resolve().parent / ".." / "saved_midi_files" / "xoutput.mid").resolve()
    midi_out = FileOut(filename=filename, device_name=device_name, send_clock=True,
                       virtual=False, ticks_per_beat=480)

    assert midi_out