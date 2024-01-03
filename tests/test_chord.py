"""
Unit tests for Chord
"""

import isobar as iso

def test_chord():
    chord = iso.Chord([3, 4, 3])
    assert chord.intervals == [3, 4, 3]
    assert chord.root == 0
    assert chord.semitones == [0, 3, 7, 10]

    chord = iso.Chord([3, 4, 3], root=3)
    assert chord.intervals == [3, 4, 3]
    assert chord.root == 3
    assert chord.semitones == [3, 6, 10, 13]
