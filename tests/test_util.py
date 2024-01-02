""" Unit tests for Utils """

import isobar as iso

def test_util_midi_note_to_note_name():
    assert iso.midi_note_to_note_name(60 - 60) == 'C-1'
    assert iso.midi_note_to_note_name(60 - 48) == 'C0'
    assert iso.midi_note_to_note_name(60 - 36) == 'C1'
    assert iso.midi_note_to_note_name(60 - 24) == 'C2'
    assert iso.midi_note_to_note_name(60 - 12) == 'C3'
    assert iso.midi_note_to_note_name(58) == 'A#3'
    assert iso.midi_note_to_note_name(60) == 'C4'
    assert iso.midi_note_to_note_name(61) == 'C#4'
    assert iso.midi_note_to_note_name(60 + 12) == 'C5'
    assert iso.midi_note_to_note_name(60 + 24) == 'C6'
    assert iso.midi_note_to_note_name(60 + 36) == 'C7'
    assert iso.midi_note_to_note_name(60 + 48) == 'C8'
    assert iso.midi_note_to_note_name(60 + 60) == 'C9'

def test_util_note_name_to_midi_note():
    assert iso.note_name_to_midi_note('C-1') == 60 - 60
    assert iso.note_name_to_midi_note('C0') == 60 - 48
    assert iso.note_name_to_midi_note('C1') == 60 - 36
    assert iso.note_name_to_midi_note('C2') == 60 - 24
    assert iso.note_name_to_midi_note('C3') == 60 - 12
    assert iso.note_name_to_midi_note('C4') == 60
    assert iso.note_name_to_midi_note('C5') == 60 + 12
    assert iso.note_name_to_midi_note('C6') == 60 + 24
    assert iso.note_name_to_midi_note('C7') == 60 + 36
    assert iso.note_name_to_midi_note('C8') == 60 + 48
    assert iso.note_name_to_midi_note('C9') == 60 + 60

    assert iso.note_name_to_midi_note('C') == 0
    assert iso.note_name_to_midi_note('C#4') == 61
    assert iso.note_name_to_midi_note('Db4') == 61

    # function combined with inverted function
    assert iso.note_name_to_midi_note(iso.midi_note_to_note_name(60)) == 60
