import pytest
import isobar as iso

def test_pdegree():
    a = iso.PDegree(iso.PSequence([0, 1, -1, None, 7], 1))
    assert list(a) == [0, 2, -1, None, 12]

    # Test on array values
    a = iso.PDegree(iso.PSequence([[0, 1], [2, 3], [None, -1]], 1))
    assert list(a) == [(0, 2), (4, 5), (None, -1)]

def test_pfilterbykey():
    a = iso.PFilterByKey(iso.PSequence([0, 1, 2, 3, -1, None, 2], 1), iso.Key("C", "major"))
    assert list(a) == [0, None, 2, None, -1, None, 2]

def test_pnearest():
    a = iso.PNearestNoteInKey(iso.PSequence([0, 1, 2, 3, -1, None, 12.5], 1), iso.Key("C", "major"))
    assert list(a) == [0, 0, 2, 2, -1, None, 12]

def test_pmiditofrequency():
    a = iso.PMidiNoteToFrequency(iso.PSequence([0, 60, 60.5, None], 1))
    assert list(a) == [8.175798915643707, 261.6255653005986, 269.2917795270241, None]
