""" Unit tests for Utils """

from isobar import midi_note_to_note_name, note_name_to_midi_note, frequency_to_midi_note, midi_note_to_frequency
import numpy as np
import numpy.testing as npt

def test_util_midi_note_to_note_name():
    assert midi_note_to_note_name(60 - 60) == 'C-1'
    assert midi_note_to_note_name(60 - 48) == 'C0'
    assert midi_note_to_note_name(60 - 36) == 'C1'
    assert midi_note_to_note_name(60 - 24) == 'C2'
    assert midi_note_to_note_name(60 - 12) == 'C3'
    assert midi_note_to_note_name(58) == 'A#3'
    assert midi_note_to_note_name(60) == 'C4'
    assert midi_note_to_note_name(61) == 'C#4'
    assert midi_note_to_note_name(60 + 12) == 'C5'
    assert midi_note_to_note_name(60 + 24) == 'C6'
    assert midi_note_to_note_name(60 + 36) == 'C7'
    assert midi_note_to_note_name(60 + 48) == 'C8'
    assert midi_note_to_note_name(60 + 60) == 'C9'

def test_util_note_name_to_midi_note():
    assert note_name_to_midi_note('C-1') == 60 - 60
    assert note_name_to_midi_note('C0') == 60 - 48
    assert note_name_to_midi_note('C1') == 60 - 36
    assert note_name_to_midi_note('C2') == 60 - 24
    assert note_name_to_midi_note('C3') == 60 - 12
    assert note_name_to_midi_note('C4') == 60
    assert note_name_to_midi_note('C5') == 60 + 12
    assert note_name_to_midi_note('C6') == 60 + 24
    assert note_name_to_midi_note('C7') == 60 + 36
    assert note_name_to_midi_note('C8') == 60 + 48
    assert note_name_to_midi_note('C9') == 60 + 60

    assert note_name_to_midi_note('C') == 0
    assert note_name_to_midi_note('C#4') == 61
    assert note_name_to_midi_note('Db4') == 61

    # function combined with inverted function
    assert note_name_to_midi_note(midi_note_to_note_name(60)) == 60

def test_util_frequency_to_midi_note():
    npt.assert_almost_equal(frequency_to_midi_note(261.6255653005986), 60)
    npt.assert_almost_equal(frequency_to_midi_note(440), 69)
    npt.assert_allclose(frequency_to_midi_note([440, 261.6255653005986, -1], omit_invalid_frequencies=True), [69, 60])
    assert frequency_to_midi_note([-1, -2], omit_invalid_frequencies=False) == [None, None]
    assert type(frequency_to_midi_note([440, 880])) == list
    assert type(frequency_to_midi_note(np.array([440, 880]))) == np.ndarray

def test_util_midi_note_to_frequency():
    npt.assert_almost_equal(midi_note_to_frequency(60), 261.6255653005986)
    npt.assert_almost_equal(midi_note_to_frequency(69), 440)
    assert midi_note_to_frequency([None, None]) == [None, None]
    assert type(midi_note_to_frequency([69, 60])) == list
    assert type(midi_note_to_frequency(np.array([69, 60]))) == np.ndarray