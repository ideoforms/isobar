""" Unit tests for Key """

import isobar as iso
import pytest

def test_key_defaults():
    a = iso.Key()
    assert a.get(0) == 0
    assert a.get(1) == 2

def test_key_eq():
    a = iso.Key()
    b = iso.Key(0, iso.Scale([0, 2, 4, 5, 7, 9, 11]))
    assert a == b
    c = iso.Key(0, iso.Scale([0, 2, 3, 5, 7, 9, 11]))
    assert a != c
    d = iso.Key(1, iso.Scale([0, 2, 4, 5, 7, 9, 11]))
    assert a != d

def test_key_invalid():
    with pytest.raises(iso.UnknownNoteName):
        a = iso.Key("X", "major")
    with pytest.raises(iso.UnknownNoteName):
        a = iso.Key("H", "minor")
    with pytest.raises(iso.UnknownScaleName):
        a = iso.Key("C", "mundo")

def test_key_get():
    a = iso.Key("C", "major")
    assert a.get(0) == a[0] == 0
    assert a.get(1) == a[1] == 2
    assert a.get(2) == a[2] == 4
    assert a.get(7) == a[7] == 12
    assert a.get(-1) == a[-1] == -1

def test_key_contains():
    a = iso.Key("C", "major")
    assert 0 in a
    assert 1 not in a
    assert 2 in a
    assert 3 not in a
    assert 4 in a
    assert 12 in a
    assert 13 not in a
    assert -1 in a
    assert None in a

def test_key_semitones():
    a = iso.Key("C", "minor")
    assert a.semitones == [0, 2, 3, 5, 7, 8, 10]

def test_key_nearest_note():
    a = iso.Key("C", iso.Scale([0, 2, 3, 5, 7, 9]))
    assert a.nearest_note(-3) == -3
    assert a.nearest_note(-2) == -3
    assert a.nearest_note(-1) == 0
    assert a.nearest_note(0) == 0
    assert a.nearest_note(1) == 0
    assert a.nearest_note(2) == 2
    assert a.nearest_note(3) == 3
    assert a.nearest_note(4) == 3
    assert a.nearest_note(5) == 5
    assert a.nearest_note(6) == 5
    assert a.nearest_note(7) == 7
    assert a.nearest_note(8) == 7
    assert a.nearest_note(9) == 9
    assert a.nearest_note(10) == 9
    assert a.nearest_note(11) == 12
    assert a.nearest_note(13) == 12
    assert a.nearest_note(14) == 14
    assert a.nearest_note(60) == 60
    assert a.nearest_note(61) == 60

    a = iso.Key("F#", "major")
    assert a.nearest_note(0) == 1
    assert a.nearest_note(6) == 6
    assert a.nearest_note(17) == 17
    assert a.nearest_note(18) == 18

def test_key_voiceleading():
    pass

def test_key_distance():
    a = iso.Key("C", "minor")
    b = iso.Key("C", "major")
    assert a.distance(b) == 3

def test_key_random():
    a = iso.Key.random()
    assert a.tonic >= 0 and a.tonic < 12
    assert len(a.semitones) > 0
    assert len(a.semitones) <= 12
    assert all(type(n) is int for n in a.semitones)
