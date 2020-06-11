import pytest
import isobar as iso

def test_pchanged():
    a = iso.PSequence([1, 1, 2, 3, 3, "a", "a", "b", None, None, 1], 1)
    b = iso.PChanged(a)

    assert next(b) == 0
    assert next(b) == 1
    list(b)
    assert list(b) == [0, 1, 1, 0, 1, 0, 1, 1, 0, 1]

def test_pdiff():
    a = iso.PSequence([4, 5, 5, 1, -2, None, 1, 1.5], 1)
    b = iso.PDiff(a)

    assert next(b) == 1
    assert next(b) == 0
    list(b)
    assert list(b) == [1, 0, -4, -3, None, None, 0.5]

def test_pabs():
    a = iso.PSequence([4, 5, 1, -2, None, 1, -1.5], 1)
    b = iso.PAbs(a)
    assert list(b) == [4, 5, 1, 2, None, 1, 1.5]

def test_pnorm():
    pass

def test_pmap():
    a = iso.PSequence([4, 5, 1, -2, 1, -1.5], 1)
    b = iso.PMap(a, lambda value: value * value)
    assert list(b) == [16, 25, 1, 4, 1, 2.25]

def test_pmap_args():
    a = iso.PSequence([4, 5, 1, -2, 1, -1.5], 1)
    b = iso.PMap(a, lambda x, y: x + y, iso.PSeries())
    assert list(b) == [4, 6, 3, 1, 5, 3.5]

def test_pmapenumerated():
    a = iso.PSequence([4, 5, 1, -2, 1, -1.5], 1)
    b = iso.PMapEnumerated(a, lambda index, value: index + value)
    assert list(b) == [4, 6, 3, 1, 5, 3.5]

def test_plinlin():
    a = iso.PSequence([4, 5, 1, -2, 1, -1.5], 1)
    b = iso.PLinLin(a, 0, 10, 100, 200)
    assert list(b) == [140, 150, 110, 80, 110, 85]

def test_plinexp():
    pass

def test_pexplin():
    pass

def test_pround():
    # Note that Python3 rounds x.5 to the nearest even number
    a = iso.PSequence([0, 0.1, 0.5, 1, 1.5, -3.9], 1)
    b = iso.PMap(a, lambda c: round(c))
    assert list(b) == [0, 0, 0, 1, 2, -4]

def test_pwrap():
    a = iso.PSequence([0, 0.1, 0.5, 1, 1.5, -3.9], 1)
    b = iso.PWrap(a, 1, 2)
    assert list(b) == [1.0, 1.1, 1.5, 1, 1.5, 1.1]

def test_pindexof():
    a = iso.PSequence([1, 2, 3, 7, None, 1], 1)
    b = iso.PSequence([[ 1, 2, 3, 4], [ 5, 6, 7, 8 ]])
    c = iso.PIndexOf(b, a)
    assert list(c) == [0, None, 2, 2, None, None]
