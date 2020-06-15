""" Unit tests for iso """

import pytest
import isobar as iso

def test_pattern_stopiteration():
    p = iso.PSequence([1, 2, 3], 1)
    assert next(p) == 1
    assert next(p) == 2
    assert next(p) == 3
    with pytest.raises(StopIteration):
        next(p)

def test_pattern_len():
    p = iso.PSequence([1, 2, 3], 1)
    assert len(p) == 3

    p = iso.PSequence([1, 2, 3], 0)
    assert len(p) == 0

def test_pattern_iter():
    p = iso.PSequence([1, 2, 3], 1)
    i = iter(p)
    o = list(i)
    assert o == [1, 2, 3]

def test_pattern_all():
    p = iso.PSequence([1, 2, 3], 1)
    assert p.all() == [1, 2, 3]

    # check that the sequence is reset afterwards
    assert p.all() == [1, 2, 3]

    p = iso.PSequence([1, 2, 3], 1)
    assert p.all(2) == [1, 2]

    p1 = iso.PSequence([1, 2, 3], 1)
    p2 = iso.PSequence([1, 2, 3, 4], 1)
    p = p1 + p2
    assert p.all() == [2, 4, 6]

def test_pattern_reset():
    p = iso.PSequence([1, 2, 3], 1)
    assert next(p) == 1
    assert next(p) == 2
    p.reset()
    assert list(p) == [1, 2, 3]

def test_pattern_append():
    p1 = iso.PSequence([1, 2, 3], 1)
    p2 = iso.PSequence([1, 2, 3], 1)
    p3 = p1.append(p2)
    assert p3.all() == [1, 2, 3, 1, 2, 3]

def test_pattern_timeline():
    p = iso.PSequence([1, 2, 3], 1)
    assert p.timeline is None
    # TODO test if it works in situ

def test_pattern_copy():
    p1 = iso.PSequence([1, 2, 3], 1)
    p2 = p1.copy()
    assert p1.all() == p2.all() == [1, 2, 3]

    p1 = iso.PSequence([1, 2, 3], 1)
    next(p1)
    p2 = p1.copy()
    assert p1.all() == p2.all() == [2, 3]

def test_pattern_value():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert iso.Pattern.value(p1) == 1

    p1 = iso.PSequence([1, 2, 3], 1)
    p2 = iso.PSequence([ p1 ])
    assert iso.Pattern.value(p2) == 1

    assert iso.Pattern.value(1) == 1
    assert iso.Pattern.value([1]) == [1]
    assert iso.Pattern.value(None) is None

def test_pattern_patternify():
    p = iso.Pattern.pattern(1)
    assert type(p) is iso.PConstant
    assert next(p) == 1

    p = iso.Pattern.pattern([1, 2, 3])
    assert type(p) is iso.PConstant
    assert list(next(p)) == [1, 2, 3]

    p = iso.Pattern.pattern(None)
    assert type(p) is iso.PConstant
    assert next(p) is None

    p = iso.Pattern.pattern(iso.PSequence([1, 2, 3], 1))
    assert type(p) is iso.PSequence
    assert list(p) == [1, 2, 3]