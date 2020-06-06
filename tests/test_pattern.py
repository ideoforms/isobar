""" Unit tests for isobar """

import pytest
import isobar
import time
import os

def test_pattern_stopiteration():
    p = isobar.PSequence([1, 2, 3], 1)
    assert next(p) == 1
    assert next(p) == 2
    assert next(p) == 3
    with pytest.raises(StopIteration):
        next(p)

def test_pattern_len():
    p = isobar.PSequence([1, 2, 3], 1)
    assert len(p) == 3

def test_pattern_iter():
    p = isobar.PSequence([1, 2, 3], 1)
    i = iter(p)
    o = list(i)
    assert o == [1, 2, 3]

def test_pattern_all():
    p = isobar.PSequence([1, 2, 3], 1)
    assert p.all() == [1, 2, 3]

def test_pattern_reset():
    p = isobar.PSequence([1, 2, 3], 1)
    assert next(p) == 1
    assert next(p) == 2
    p.reset()
    assert next(p) == 1
    assert next(p) == 2
    assert next(p) == 3
    with pytest.raises(StopIteration):
        next(p)

def test_pattern_append():
    p1 = isobar.PSequence([1, 2, 3], 1)
    p2 = isobar.PSequence([1, 2, 3], 1)
    p3 = p1.append(p2)
    assert p3.all() == [1, 2, 3, 1, 2, 3]

def test_pattern_timeline():
    p = isobar.PSequence([1, 2, 3], 1)
    assert p.timeline is None
    # TODO test if it works in situ

def test_pattern_copy():
    p1 = isobar.PSequence([1, 2, 3], 1)
    p2 = p1.copy()
    assert p1.all() == p2.all() == [1, 2, 3]

def test_pattern_value():
    p1 = isobar.PSequence([1, 2, 3], 1)
    p2 = isobar.PSequence([ p1 ])
    assert isobar.Pattern.value(p2) == 1