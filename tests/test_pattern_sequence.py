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

def test_pinterpolate():
    a = iso.PSequence([0, 1, 2], 1)
    steps = iso.PSequence([4, 2], 1)
    b = iso.PInterpolate(a, steps, iso.INTERPOLATION_NONE)
    assert list(b) == [0, 0, 0, 0, 1, 1, 2]

    a = iso.PSequence([0, 1, 2], 1)
    steps = iso.PSequence([4, 2], 1)
    b = iso.PInterpolate(a, steps, iso.INTERPOLATION_LINEAR)
    assert list(b) == [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]

    b = iso.PInterpolate(iso.PSequence([0, 1, 2]), iso.PSequence([2, 2]), 99)
    print(next(b))
    with pytest.raises(ValueError):
        next(b)

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
    a = iso.PArpeggiator([0, 1, 2, 3], iso.PArpeggiator.UP)
    assert a.nextn(16) == [0, 1, 2, 3]

    a = iso.PArpeggiator([0, 1, 2, 3], iso.PArpeggiator.DOWN)
    assert a.nextn(16) == [3, 2, 1, 0]

    a = iso.PArpeggiator([0, 1, 2, 3], iso.PArpeggiator.CONVERGE)
    assert a.nextn(16) == [0, 3, 1, 2]

    a = iso.PArpeggiator([0, 1, 2, 3, 4], iso.PArpeggiator.CONVERGE)
    assert a.nextn(16) == [0, 4, 1, 3, 2]

    a = iso.PArpeggiator([0, 1, 2, 3], iso.PArpeggiator.CONVERGE)
    assert a.nextn(16) == [0, 3, 1, 2]

    a = iso.PArpeggiator([0, 1, 2, 3, 4], iso.PArpeggiator.DIVERGE)
    assert a.nextn(16) == [2, 1, 3, 0, 4]

    a = iso.PArpeggiator([0, 1, 2, 3], iso.PArpeggiator.DIVERGE)
    assert a.nextn(16) == [1, 2, 0, 3]

    a = iso.PArpeggiator([0, 1, 2, 3, 4], iso.PArpeggiator.RANDOM)
    a.seed(0)
    a.reset()
    assert a.nextn(16) == [2, 1, 0, 4, 3]

def test_peuclidean():
    a = iso.PEuclidean(4, 7, 0)
    assert a.nextn(16) == [1, None, 1, None, 1, None, 1, 1, None, 1, None, 1, None, 1, 1, None]

    a = iso.PEuclidean(4, iso.PSequence([7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4], 1))
    assert a.nextn(19) == [1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, 1, 1, 1, 1]

def test_ppermut():
    a = iso.PPermut(iso.PSequence([1, 11, 111]), 3)
    assert list(a) == [1, 11, 111, 1, 111, 11, 11, 1, 111, 11, 111, 1, 111, 1, 11, 111, 11, 1]

def test_ppatterngeneratoraction():
    n = 0

    def generate():
        nonlocal n
        n += 1
        if n == 1:
            return iso.PSequence([0], 2)
        elif n == 2:
            return iso.PSequence([1, 2], 1)
        else:
            return None

    a = iso.PPatternGeneratorAction(generate)
    assert next(a) == 0
    assert next(a) == 0
    assert next(a) == 1
    assert next(a) == 2
    with pytest.raises(StopIteration):
        next(a)

def test_psequenceaction():
    a = iso.PSequenceAction([1, 2, 3], lambda a: list(reversed(a)), 4)
    assert list(a) == [1, 2, 3, 3, 2, 1, 1, 2, 3, 3, 2, 1]
