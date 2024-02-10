""" Unit tests for Key """

import os
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

    for key in events.keys():
        assert isinstance(d[key], iso.PSequence)
        if key == iso.EVENT_NOTE:
            assert list(d[key]) == [e or 0 for e in list(events[key])]
        elif key == iso.EVENT_DURATION:
            assert pytest.approx(list(d[key]), rel=0.01) == list(events[key])
        elif key == iso.EVENT_GATE:
            assert pytest.approx(list(d[key]), rel=0.3) == list(events[key])
        elif key == iso.EVENT_AMPLITUDE:
            amp = [am if nt else 0 for (am, nt) in zip(events[key].sequence, events[iso.EVENT_NOTE].sequence)]
            assert list(d[key]) == amp
        else:
            assert list(d[key]) == list(events[key])

    os.unlink("output.mid")

# TEST_FILENAME = "test.mid"
#
# # Fixture to mock mido.MidiFile
# @pytest.fixture
# def mock_midi_file(monkeypatch):
#     def _mock_midi_file(filename):
#         monkeypatch.setattr("mido.MidiFile", MagicMock(return_value=None))
#     return _mock_midi_file
#
# @pytest.mark.parametrize("objects, track_idx, expected_calls, test_id", [
#     # Happy path tests
#     ([MidiMetaMessageTempo(tempo=500000, location=0)], 0, {'set_tempo': 1, 'text': 1}, 'happy_path_tempo'),
    # ([MidiMessageControl(cc=1, value=64, channel=0, location=0)], 0, {'control': 1}, 'happy_path_control'),
    # ([MidiMessageProgram(program=1, channel=0, location=0)], 0, {'program_change': 1}, 'happy_path_program'),
    # ([MidiMessagePitch(pitch=8192, channel=0, location=0)], 0, {'pitch_bend': 1}, 'happy_path_pitch'),
    # ([MidiMessageAfter(value=64, channel=0, location=0)], 0, {'aftertouch': 1}, 'happy_path_after'),
    # ([MidiMessagePoly(note=60, value=64, channel=0, location=0)], 0, {'polytouch': 1}, 'happy_path_poly'),

    # Edge cases
    # ([], 0, {}, 'edge_case_empty_list'),
    # (None, 0, {}, 'edge_case_none_object'),

    # Error cases
    # Assuming that the error cases are handled outside of this function
# ])
#
# def test_midi_message_obj(mock_midi_file, objects, track_idx, expected_calls, test_id):
#     # Arrange
#     timeline_inner_mock = Mock()
#     timeline_inner_mock.output_device = Mock()
#     timeline_inner_mock.output_device.miditrack = {0: []}
#     timeline_inner_mock.output_device.get_channel_track = Mock(return_value=0)
#     set_tempo_callback_mock = Mock()
#
#     # Act
#     mock_midi_file(TEST_FILENAME)
#     midi_input_device = MidiFileInputDevice(TEST_FILENAME)
#     midi_input_device.midi_message_obj(timeline_inner_mock, objects=objects, track_idx=track_idx)
#
#     # Assert
#     if 'set_tempo' in expected_calls:
#         assert timeline_inner_mock.set_tempo.call_count == expected_calls['set_tempo']
#         set_tempo_callback_mock.assert_called_once()
#     if 'text' in expected_calls:
#         assert len(timeline_inner_mock.output_device.miditrack[0]) == expected_calls['text']
#     if 'control' in expected_calls:
#         assert timeline_inner_mock.output_device.control.call_count == expected_calls['control']
#     if 'program_change' in expected_calls:
#         assert timeline_inner_mock.output_device.program_change.call_count == expected_calls['program_change']
#     if 'pitch_bend' in expected_calls:
#         assert timeline_inner_mock.output_device.pitch_bend.call_count == expected_calls['pitch_bend']
#     if 'aftertouch' in expected_calls:
#         assert timeline_inner_mock.output_device.aftertouch.call_count == expected_calls['aftertouch']
#     if 'polytouch' in expected_calls:
#         assert timeline_inner_mock.output_device.polytouch.call_count == expected_calls['polytouch']
#
#     os.unlink("output.mid")