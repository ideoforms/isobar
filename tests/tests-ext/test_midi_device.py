from isobar_ext.io import  MidiFileOutputDevice


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