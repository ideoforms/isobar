from unittest.mock import Mock

import pytest

from isobar_ext.io.midifile.input import MidiFileInputDevice
from isobar_ext.io.midimessages import (
    MidiMetaMessageTempo, MidiMetaMessageKey, MidiMetaMessageTimeSig,
    MidiMetaMessageTrackName, MidiMetaMessageMidiPort, MidiMetaMessageEndTrack, MidiMessageControl,
    MidiMessageProgram, MidiMessagePitch, MidiMessagePoly, MidiMessageAfter
)
from isobar_ext.io.midinote import MidiNote


# Test MidiNote initialization and attributes
@pytest.mark.parametrize("test_id, pitch, velocity, location, channel, duration", [
    ("happy_path_1", 60, 100, 0, 1, 1),
    ("happy_path_2", 127, 127, 10, 0, 0.5),
    ("edge_case_min_values", 0, 0, 0, 0, None),
    ("edge_case_max_values", 15, 127, 127, 10, 1000),
    ("error_case_invalid_pitch", 128, 100, 0, 1, 1),
    ("error_case_invalid_velocity", 60, 128, 0, 1, 1),
    ("error_case_negative_channel", 60, 128, 0, -1, 1),
    ("error_case_channel_over_15", 60, 128, 0, 16, 1),
])
def test_cust_midi_note(test_id, pitch, velocity, location, channel, duration):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiNote(pitch, velocity, location, channel, duration)
    else:
        # Act
        note = MidiNote(pitch, velocity, location, channel, duration)

        # Assert
        assert note.channel == channel
        assert note.pitch == pitch
        assert note.velocity == velocity
        assert note.location == location
        assert note.duration == duration


# Test MidiMetaMessageTempo to_meta_message method
@pytest.mark.parametrize("test_id, tempo, location, time", [
    ("happy_path_1", 500000, 0, 0),
    ("happy_path_2", 250000, 10, 1),
    ("edge_case_min_tempo", 0, 0, 0),
    ("edge_case_max_tempo", 16777215, 1000, 10),
    ("error_case_invalid_tempo", -1, 0, 0),
])
def test_midi_meta_message_tempo(test_id, tempo, location, time):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageTempo(tempo, location, time=time)
    else:
        tempo_message = MidiMetaMessageTempo(tempo, location, time=time)

        # Act
        meta_message = tempo_message.to_meta_message()

        # Assert
        assert meta_message.tempo == tempo
        assert meta_message.time == time
        assert meta_message.type == 'set_tempo'


# Test MidiMetaMessageKey to_meta_message method
@pytest.mark.parametrize("test_id, key, location, time", [
    ("happy_path_1", "C", 0, 0),
    ("happy_path_2", "F#", 10, 1),
    ("error_case_invalid_key", "H", 0, 0),
])
def test_midi_meta_message_key(test_id, key, location, time):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageKey(key, location, time=time)
    else:
        key_message = MidiMetaMessageKey(key, location, time=time)

        # Act
        meta_message = key_message.to_meta_message()

        # Assert
        assert meta_message.key == key
        assert meta_message.time == time
        assert meta_message.type == 'key_signature'


# Test MidiMetaMessageTimeSig to_meta_message method
@pytest.mark.parametrize(
    "test_id, numerator, denominator, clocks_per_click, notated_32nd_notes_per_beat, location, time", [
        ("happy_path_1", 4, 4, 24, 8, 0, 0),
        ("happy_path_2", 3, 8, 12, 8, 10, 1),

        ("min_numerator", 1, 4, 1, 1, 0, 0),
        ("min_denominator", 4, 1, 1, 1, 0, 0),
        ("min_clocks_per_click", 4, 4, 1, 1, 0, 0),
        ("min_notated_32nd_notes_per_beat", 4, 4, 1, 1, 0, 0),

        ("max_numerator", 255, 4, 1, 1, 0, 0),
        ("max_denominator", 4, 2 ** 255, 1, 1, 0, 0),
        ("max_clocks_per_click", 4, 4, 255, 1, 0, 0),
        ("max_notated_32nd_notes_per_beat", 4, 4, 1, 255, 0, 0),

        ("error_case_invalid_numerator", -1, 4, 24, 8, 0, 0),
        ("error_case_invalid_denominator", 4, -1, 24, 8, 0, 0),
        ("error_case_non_power_of_two_denominator", 4, 5, 24, 8, 0, 0),
        ("error_case_negative_clocks_per_click", 4, 4, -1, 8, 0, 0),
        ("error_case_negative_notated_32nd_notes_per_beat", 4, 4, 24, -1, 0, 0),
        ("error_case_over_max_denominator", 4, 2 ** 256, 24, 8, 0, 0),
        ("error_case_over_max_clocks_per_click", 4, 4, 256, 8, 0, 0),
        ("error_case_over_max_notated_32nd_notes_per_beat", 4, 4, 24, 256, 0, 0)

    ])
def test_midi_meta_message_time_sig(test_id, numerator, denominator, clocks_per_click, notated_32nd_notes_per_beat,
                                    location, time):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageTimeSig(numerator, denominator, clocks_per_click, notated_32nd_notes_per_beat, location,
                                   time=time)
    else:
        time_sig_message = MidiMetaMessageTimeSig(numerator, denominator, clocks_per_click, notated_32nd_notes_per_beat,
                                                  location, time=time)

        # Act
        meta_message = time_sig_message.to_meta_message()

        # Assert
        assert meta_message.numerator == numerator
        assert meta_message.denominator == denominator
        assert meta_message.clocks_per_click == clocks_per_click
        assert meta_message.notated_32nd_notes_per_beat == notated_32nd_notes_per_beat
        assert meta_message.time == time
        assert meta_message.type == 'time_signature'


@pytest.mark.parametrize("test_id, channel, cc, value, location, time, track_idx", [
    ("happy_path_1", 1, 64, 127, 2.0, 0, 0),
    ("happy_path_2", 15, 120, 0, 4.5, 10, 1),
    ("happy_path_3", 8, 50, 75, 1.0, 3, 5),
    ("edge_case_channel_0", 0, 100, 64, 1.5, 5, 2),
    ("edge_case_max_cc_value_and_value", 1, 127, 127, 0.0, 2, 3),
    ("edge_case_negative_location", 8, 50, 75, -1.0, 0, 4),
    ("edge_case_max_channel", 15, 60, 100, 3.5, 8, 5),
    ("edge_case_max_program_value", 14, 80, 127, 2.5, 6, 7),
    ("edge_case_zero_track_idx", 10, 40, 50, 1.0, 3, 0),
    ("edge_case_zero_track_idx", 12, 90, 120, 4.0, 12, 0),
    ("error_case_invalid_channel", -1, 75, 110, 2.0, 0, 0),
    ("error_case_invalid_cc", 6, 150, 180, 5.0, 15, 2),
    ("error_case_invalid_value", 9, 100, 300, 3.0, 10, 4),
    ("error_case_negative_time", 7, 45, 80, 1.5, -2, 1),
    ("error_case_negative_track_idx", 11, 30, 40, 0.5, 2, -3),
    # Add more test cases as needed
])
def test_midi_message_control(test_id, channel, cc, value, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMessageControl(channel, cc, value, location, time, track_idx)
    else:
        # Act
        midi_message_control = MidiMessageControl(channel, cc, value, location, time, track_idx)

        # Assert
        assert midi_message_control.channel == channel
        assert midi_message_control.cc == cc
        assert midi_message_control.value == value
        assert midi_message_control.location == location
        assert midi_message_control.time == time
        assert midi_message_control.track_idx == track_idx


@pytest.mark.parametrize("test_id, channel, program, location, time, track_idx", [
    ("happy_path_1", 1, 64, 2.0, 0, 0),
    ("happy_path_2", 15, 127, 4.5, 10, 1),
    ("edge_case_channel_0", 0, 100, 1.5, 5, 2),
    ("edge_case_max_channel_value", 15, 75, 2.0, 0, 0),
    ("edge_case_max_program_value", 8, 255, 0.1, 2, 3),
    ("edge_case_min_channel", 1, 75, 2.0, 0, 0),
    ("edge_case_min_program", 4, 0, 2.0, 0, 0),
    ("error_case_negative_location", 8, 50, -1.0, 0, 4),
    ("error_case_invalid_channel", 16, 50, 3.0, 0, 0),
    ("error_case_invalid_program", 1, 256, 2.0, 0, 0),
    ("error_case_negative_time", 4, 75, 2.0, -1.0, 0),
    ("error_case_negative_track_idx", 4, 75, 2.0, 0, -1),
    ("error_case_negative_program", 4, -75, 2.0, 0, 0),

])
def test_midi_message_program(test_id, channel, program, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMessageProgram(channel, program, location, time, track_idx)
    else:
        # Act
        midi_program_message = MidiMessageProgram(channel, program, location, time, track_idx)

        # Assert
        assert midi_program_message.channel == channel
        assert midi_program_message.program == program
        assert midi_program_message.location == location
        assert midi_program_message.time == time
        assert midi_program_message.track_idx == track_idx


@pytest.mark.parametrize("test_id, channel, pitch, location, time, track_idx", [
    ("happy_path_1", 1, 0, 2.0, 0, 0),
    ("happy_path_2", 15, 8192, 4.5, 10, 1),
    ("edge_case_channel_0", 0, 500, 1.5, 5, 2),
    ("edge_case_max_channel_value", 15, -3000, 2.0, 0, 0),
    ("edge_case_max_pitch_value", 8, 8192, 0.0, 2, 3),
    ("edge_case_min_channel", 1, 75, 2.0, 0, 0),
    ("edge_case_min_pitch", 4, -8192, 2.0, 0, 0),
    ("edge_case_min_location", 4, 75, 0.0, 0, 0),
    ("edge_case_min_time", 4, 75, 2.0, 0, 0),
    ("error_case_negative_location", 8, 50, -1.0, 0, 4),
    ("error_case_invalid_channel", 16, 50, 3.0, 0, 0),
    ("error_case_invalid_pitch", 4, 9000, 2.0, 0, 0),
    ("error_case_negative_time", 4, 75, -1.0, 0, 0),
    ("error_case_negative_track_idx", 4, 75, 2.0, 0, -1),

])
def test_midi_message_pitch(test_id, channel, pitch, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMessagePitch(channel, pitch, location, time, track_idx)
    else:
        # Act
        midi_pitch_message = MidiMessagePitch(channel, pitch, location, time, track_idx)

        # Assert
        assert midi_pitch_message.channel == channel
        assert midi_pitch_message.pitch == pitch
        assert midi_pitch_message.location == location
        assert midi_pitch_message.time == time
        assert midi_pitch_message.track_idx == track_idx


@pytest.mark.parametrize("test_id, channel, note, value, location, time, track_idx", [
    ("happy_path_1", 1, 60, 100, 2.0, 0, 0),
    ("happy_path_2", 15, 72, 80, 4.5, 10, 1),
    ("edge_case_channel_0", 0, 64, 127, 1.5, 5, 2),
    ("edge_case_max_channel_value", 15, 64, 0, 2.0, 0, 0),
    ("edge_case_max_note_value", 8, 127, 50, 0.0, 2, 3),
    ("edge_case_max_value", 8, 60, 127, 0.0, 2, 3),
    ("error_case_negative_location", 8, 50, 75, -1.0, 0, 4),
    ("error_case_invalid_channel", 16, 50, 75, 3.0, 0, 0),
    ("error_case_invalid_note", 4, 150, 75, 2.0, 0, 0),
    ("error_case_invalid_value", 4, 50, 150, 2.0, 0, 0),
    ("error_case_negative_time", 4, 75, 2, -1.0, 0, 0),
    ("error_case_negative_track_idx", 4, 75, 2, 0, 0, -1),
    ("edge_case_min_channel", 1, 75, 2, 0, 0, 0),
    ("edge_case_min_note", 4, 0, 2, 0, 0, 0),
    ("edge_case_min_value", 4, 75, 0, 2.0, 0, 0),
    ("edge_case_min_location", 4, 75, 0, 0, 0, 0),
    ("edge_case_min_time", 4, 75, 2, 0, 0, 0),
    ("edge_case_min_track_idx", 4, 75, 2, 0, 0, 0),

])
def test_midi_message_poly(test_id, channel, note, value, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMessagePoly(channel, note, value, location, time, track_idx)
    else:
        # Act
        midi_poly_message = MidiMessagePoly(channel, note, value, location, time, track_idx)

        # Assert
        assert midi_poly_message.channel == channel
        assert midi_poly_message.note == note
        assert midi_poly_message.value == value
        assert midi_poly_message.location == location
        assert midi_poly_message.time == time
        assert midi_poly_message.track_idx == track_idx



@pytest.mark.parametrize("test_id, channel, value, location, time, track_idx", [
    ("happy_path_1", 1, 100, 2.0, 0, 0),
    ("happy_path_2", 15, 80, 4.5, 10, 1),
    ("edge_case_channel_0", 0, 127, 1.5, 5, 2),
    ("edge_case_max_channel_value", 15, 0, 2.0, 0, 0),
    ("edge_case_max_value", 8, 127, 0.0, 2, 3),
    ("error_case_negative_location", 8, 75, -1.0, 0, 4),
    ("error_case_invalid_channel", 16, 75, 3.0, 0, 0),
    ("error_case_invalid_value", 4, 150, 2.0, 0, 0),
    ("error_case_negative_time", 4, 75, 2.0, -1.0, 0),
    ("error_case_negative_track_idx", 4, 75, 2.0, 0, -1),
    ("edge_case_min_channel", 1, 75, 0.0, 0, 0),
    ("edge_case_min_value", 4, 0, 2.0, 0, 0),
    ("edge_case_min_location", 4, 75, 0.0, 0, 0),
    ("edge_case_min_time", 4, 75, 0.0, 0, 0),
    ("edge_case_min_track_idx", 4, 75, 0.0, 0, 0),

])
def test_midi_message_after(test_id, channel, value, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMessageAfter(channel, value, location, time, track_idx)
    else:
        # Act
        midi_after_message = MidiMessageAfter(channel, value, location, time, track_idx)

        # Assert
        assert midi_after_message.channel == channel
        assert midi_after_message.value == value
        assert midi_after_message.location == location
        assert midi_after_message.time == time
        assert midi_after_message.track_idx == track_idx




@pytest.mark.parametrize("test_id, name, location, time, track_idx", [
    ("happy_path_1", "Track 1", 2.0, 0, 0),
    ("happy_path_2", "Background Music", 4.5, 10, 1),
    ("edge_case_empty_name", "", 1.5, 5, 2),
    ("edge_case_max_name_length", "X" * 255, 2.0, 0, 0),
    ("error_case_negative_location", "Track 3", -1.0, 0, 4),
    ("error_case_negative_time", "Track 4", 2.0, -1.0, 0),
    ("error_case_negative_track_idx", "Track 5", 2.0, 0, -1),
    ("edge_case_min_location", "Track 6", 0.0, 0, 0),
    ("edge_case_min_time", "Track 7", 2.0, 0, 0),
    ("edge_case_min_track_idx", "Track 8", 2.0, 0, 0),

    # Additional test case for to_meta_message
    ("happy_path_to_meta_message", "Custom Track", 3.5, 15, 3),
])
def test_midi_meta_message_track_name(test_id, name, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageTrackName(name, location, time, track_idx)
    else:
        # Act
        midi_track_name_message = MidiMetaMessageTrackName(name, location, time, track_idx)

        # Assert
        assert midi_track_name_message.name == name
        assert midi_track_name_message.location == location
        assert midi_track_name_message.time == time
        assert midi_track_name_message.track_idx == track_idx
        # Additional Assert for to_meta_message
        meta_message = midi_track_name_message.to_meta_message()
        assert meta_message.name == name
        assert meta_message.time == time
        assert meta_message.type == 'track_name'


@pytest.mark.parametrize(
    "test_id, port, location, time, track_idx",
    [
        ("happy_path_1", 0, 0, 0, 0),
        ("happy_path_2", 127, 5, 10, 1),
        ("edge_case_min_port", 0, 0, 0, 0),
        ("edge_case_max_port", 255, 0, 0, 0),
        ("error_case_negative_port", -1, 0, 0, 0),
        ("error_case_over_max_port", 256, 0, 0, 0),
        ("error_case_negative_location", 0, -1, 0, 0),
        ("error_case_negative_time", 0, 0, -1, 0),
        ("error_case_negative_track_idx", 0, 0, 0, -1),
    ]
)
def test_midi_meta_message_midi_port(test_id, port, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageMidiPort(port, location, time, track_idx)
    else:
        # Act
        midi_port_message = MidiMetaMessageMidiPort(port, location, time, track_idx)

        # Assert
        assert midi_port_message.port == port
        assert midi_port_message.location == location
        assert midi_port_message.time == time
        assert midi_port_message.track_idx == track_idx

        meta_message = midi_port_message.to_meta_message()
        assert meta_message.port == port
        assert meta_message.time == time
        assert meta_message.type == 'midi_port'

@pytest.mark.parametrize(
    "test_id, location, time, track_idx",
    [
        ("happy_path_1", 0, 0, 0),
        ("happy_path_2", 5, 10, 1),
        ("edge_case_zero_location", 0, 0, 0),
        ("edge_case_zero_time", 0, 0, 0),
        ("edge_case_zero_track_idx", 0, 0, 0),
        ("error_case_negative_location", -1, 0, 0),
        ("error_case_negative_time", 0, -1, 0),
        ("error_case_negative_track_idx", 0, 0, -1),

    ]
)
def test_midi_meta_message_end_track(test_id, location, time, track_idx):
    # Arrange
    if "error_case" in test_id:
        with pytest.raises(ValueError):
            # Act
            MidiMetaMessageEndTrack(location, time, track_idx)
    else:
        # Act
        end_track_message = MidiMetaMessageEndTrack(location, time, track_idx)

        # Assert
        assert end_track_message.location == location
        assert end_track_message.time == time
        assert end_track_message.track_idx == track_idx

        meta_message = end_track_message.to_meta_message()
        assert meta_message.time == time
        assert meta_message.type == 'end_of_track'