""" Unit tests for iso """

import isobar as iso

def test_pattern_add():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 + 1.5) == [2.5, 3.5, 4.5]
    assert list(-1 + p1) == [0, 1, 2]

    p2 = iso.PSequence([2, 3, 4, 5], 1)
    assert list(p1 + p2) == [3, 5, 7]

def test_pattern_sub():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 - 0.5) == [0.5, 1.5, 2.5]
    assert list(1 + p1) == [2, 3, 4]

    p2 = iso.PSequence([2, 3, 4, 5], 1)
    assert list(p2 - p1) == [1, 1, 1]

def test_pattern_mul():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 * 1.5) == [1.5, 3.0, 4.5]
    assert list(-1 * p1) == [-1, -2, -3]

    p2 = iso.PSequence([2, 3, 4, 5], 1)
    assert list(p1 * p2) == [2, 6, 12]

def test_pattern_div():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 / 2.0) == [0.5, 1.0, 1.5]
    assert list(2 / p1) == [2, 1, 2 / 3]

    p2 = iso.PSequence([2, 4, 6, 8], 1)
    assert list(p2 / p1) == [2, 2, 2]

def test_pattern_floordiv():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 // 2) == [0, 1, 1]
    assert list(2 // p1) == [2, 1, 0]

    p2 = iso.PSequence([2, 4, 6, 8], 1)
    assert list(p2 // p1) == [2, 2, 2]

def test_pattern_mod():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 % 2) == [1, 0, 1]
    assert list(2 % p1) == [0, 0, 2]

    p2 = iso.PSequence([2, 4, 6, 8], 1)
    assert list(p2 % p1) == [0, 0, 0]

def test_pattern_pow():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 ** 2) == [1, 4, 9]
    assert list(2 ** p1) == [2, 4, 8]

    p2 = iso.PSequence([2, 4, 6, 8], 1)
    assert list(p1 ** p2) == [1, 16, 729]

def test_pattern_lshift():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 << 1) == [2, 4, 6]
    assert list(1 << p1) == [2, 4, 8]

    p2 = iso.PSequence([2, 4, 6, 8], 1)
    assert list(p2 << p1) == [4, 16, 48]

def test_pattern_rshift():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 >> 1) == [0, 1, 1]
    assert list(1 >> p1) == [0, 0, 0]

    p2 = iso.PSequence([4, 8, 16, 32], 1)
    assert list(p2 >> p1) == [2, 2, 2]

def test_pattern_eq():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 == 2) == [0, 1, 0]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 == p2) == [0, None, 1]

def test_pattern_ne():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 != 2) == [1, 0, 1]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 != p2) == [1, None, 0]

def test_pattern_gt():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 > 2) == [0, 0, 1]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 > p2) == [0, None, 0]

def test_pattern_ge():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 >= 2) == [0, 1, 1]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 >= p2) == [0, None, 1]

def test_pattern_lt():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 < 2) == [1, 0, 0]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 < p2) == [1, None, 0]

def test_pattern_le():
    p1 = iso.PSequence([1, 2, 3], 1)
    assert list(p1 <= 2) == [1, 1, 0]

    p2 = iso.PSequence([5, None, 3])
    assert list(p1 <= p2) == [1, None, 1]
