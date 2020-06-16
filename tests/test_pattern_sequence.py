import pytest
import isobar as iso

def test_psequence_ints():
    a = iso.PSequence([1, 2, 3], 1)
    assert list(a) == [1, 2, 3]

def test_psequence_tuples():
    a = iso.PSequence([(1, 2), (3, 4), (5, 6)], 2)
    assert list(a) == [(1, 2), (3, 4), (5, 6), (1, 2), (3, 4), (5, 6)]

def test_psequence_keys():
    a = iso.PSequence([iso.Key("C", "major"), iso.Key("F", "minor")], 1)
    assert list(a) == [iso.Key("C", "major"), iso.Key("F", "minor")]

def test_pseries():
    a = iso.PSeries(2, iso.PSequence([1, 2]), iso.PConstant(5))
    assert list(a) == [2, 3, 5, 6, 8]

def test_prange():
    a = iso.PRange(0, iso.PConstant(10), iso.PSequence([1, 2]))
    assert list(a) == [0, 1, 3, 4, 6, 7, 9]

def test_pgeom():
    a = iso.PGeom(1, iso.PSequence([1, 2]), 8)
    assert list(a) == [1, 1, 2, 2, 4, 4, 8, 8]

def test_pimpulse():
    a = iso.PImpulse(4)
    b = iso.PSubsequence(a, 0, 8)
    assert list(b) == [1, 0, 0, 0, 1, 0, 0, 0]

def test_ploop():
    a = iso.PSequence([1, 2, 3], 1)
    b = iso.PLoop(a, 3)
    assert list(b) == [1, 2, 3, 1, 2, 3, 1, 2, 3]

def test_ploop_bang():
    pass

def test_ppingpong():
    a = iso.PSequence([1, 2, 3], 1)
    b = iso.PPingPong(a, 2)
    assert list(b) == [1, 2, 3, 2, 1, 2, 3, 2, 1]

def test_pcreep():
    a = iso.PSequence([1, 2, 3, 4, 5], 1)
    b = iso.PCreep(a, 3, 1, 2)
    assert list(b) == [1, 2, 3, 1, 2, 3, 2, 3, 4, 2, 3, 4, 3, 4, 5, 3, 4, 5]

def test_pstutter():
    a = iso.PSequence([1, 2, 3], 1)
    b = iso.PStutter(a, 3)
    assert list(b) == [1, 1, 1, 2, 2, 2, 3, 3, 3]

def test_psubsequence():
    a = iso.PSeries()
    b = iso.PSubsequence(a, 4, 4)
    assert list(b) == [4, 5, 6, 7]

def test_preverse():
    a = iso.PSequence([1, 2, 3, 4, 5], 1)
    b = iso.PReverse(a)
    assert list(b) == [5, 4, 3, 2, 1]

def test_preset():
    a = iso.PSeries(0, 1)
    b = iso.PReset(a, iso.PImpulse(4))
    c = iso.PSubsequence(b, 0, 10)
    assert list(c) == [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]

def test_pcounter():
    a = iso.PCounter(iso.PImpulse(4))
    b = iso.PSubsequence(a, 0, 10)
    assert list(b) == [1, 1, 1, 1, 2, 2, 2, 2, 3, 3]

def test_pcollapse():
    a = iso.PSequence([1, 2, None, 3, 4, None, None, 5, 6, None], 1)
    b = iso.PCollapse(a)
    assert list(b) == [1, 2, 3, 4, 5, 6]

def test_pnorepeats():
    a = iso.PSequence([1, 2, 2, 3, 3.5, 3.5, 4, None, None, 5], 1)
    b = iso.PNoRepeats(a)
    assert list(b) == [1, 2, 3, 3.5, 4, None, 5]

def test_ppad():
    a = iso.PSequence([1, None, 2], 1)
    b = iso.PPad(a, 6)
    assert list(b) == [1, None, 2, None, None, None]

    a = iso.PSequence([1, None, 2], 1)
    b = iso.PPad(a, 3)
    assert list(b) == [1, None, 2]

def test_ppadtomultiple():
    a = iso.PSequence([1, 2, 3, 4, None, 6], 1)
    b = iso.PPadToMultiple(a, 4)
    assert list(b) == [1, 2, 3, 4, None, 6, None, None]

    a = iso.PSequence([1, None, 2], 1)
    b = iso.PPadToMultiple(a, 3)
    assert list(b) == [1, None, 2]

def test_parpeggiator():
    # TODO
    pass

def test_peuclidean():
    # TODO
    pass

def test_ppermut():
    # TODO
    pass

def test_pdecisionpoint():
    # TODO
    pass

def test_psequenceoperation():
    a = iso.PSequenceAction([1, 2, 3], lambda a: list(reversed(a)), 4)
    assert list(a) == [1, 2, 3, 3, 2, 1, 1, 2, 3, 3, 2, 1]
