import pytest
import isobar as iso

def test_pref():
    a = iso.PSequence([1, 2, 3], 1)
    b = iso.PSequence([4, 5, 6], 1)
    c = iso.PRef(a)
    assert next(c) == 1
    assert next(c) == 2
    c.pattern = b
    assert next(c) == 4
    assert next(c) == 5
    assert next(c) == 6
    with pytest.raises(StopIteration):
        next(c)

def test_pfunc():
    s = "abc"
    a = iso.PSequence([0, 1, 2], 1)
    b = iso.PFunc(lambda: s[next(a)])
    assert next(b) == 'a'
    assert next(b) == 'b'
    assert next(b) == 'c'
    with pytest.raises(StopIteration):
        next(b)

def test_parrayindex():
    ar = iso.PSequence([[0, 1, 2, 3, 4], [0, 1, 4, 9, 16]])
    a = iso.PSequence([0, 2, 4], 1)
    b = iso.PArrayIndex(a, ar)
    assert next(b) == 0
    assert next(b) == 4
    assert next(b) == 4
    with pytest.raises(StopIteration):
        next(b)

def test_pdict():
    a = iso.PDict({
        "a": iso.PSequence([1, 2, 3], 1),
        "b": 4,
        "c": None
    })
    assert list(a) == [
        {"a": 1, "b": 4, "c": None},
        {"a": 2, "b": 4, "c": None},
        {"a": 3, "b": 4, "c": None}
    ]

    a = iso.PDict([{"a": 1}, {"a": 2, }, {"a": 3}])
    b = a["a"].copy()
    assert list(b) == [1, 2, 3]
    assert list(a) == [{"a": 1}, {"a": 2}, {"a": 3}]

def test_pdictkey():
    d1 = {"foo": "bar", "baz": "buzz"}
    d2 = {"foo": "boo", "baz": "bez"}
    a = iso.PSequence(["foo", "baz"], 1)
    b = iso.PDictKey(a, iso.PSequence([d1, d2]))
    assert list(b) == ["bar", "bez"]

def test_pconcatenate():
    a = iso.PSequence([1, 2], 1)
    b = iso.PSequence([3, 4], 1)
    c = iso.PSequence([5], 1)
    d = iso.PConcatenate([a, b, c])
    assert list(d) == [1, 2, 3, 4, 5]