import pytest
import isobar as iso

@pytest.fixture(autouse=True)
def test_seed_random():
    iso.random_seed(0)

def test_pwhite():
    a = iso.PWhite(iso.PConstant(5), iso.PConstant(10))
    assert a.nextn(10) == [8, 8, 5, 7, 9, 8, 8, 7, 8, 7]

    a = iso.PWhite(iso.PConstant(-1.0), iso.PConstant(1.0))
    assert a.nextn(10) == [0.1667640789100624, 0.8162257703906703, 0.009373711634780513, -0.43632431120059234, 0.5116084083144479, 0.23673799335066326, -0.4989873172751189, 0.8194925119364802, 0.9655709520753062, 0.6204344719931791]

def test_pbrown():
    a = iso.PBrown(0, iso.PConstant(5), iso.PConstant(-5), iso.PConstant(5))
    assert a.nextn(20) == [0, 1, 2, -3, -4, -1, 1, 2, 1, 3, 3, 5, 3, 5, 2, 1, -2, -5, -1, -2]

    a = iso.PBrown(0.0, 1.0, -1.0, 1.0)
    assert a.nextn(10) == [0.0, 0.9655709520753062, 1.0, 1.0, 0.6202951386386653, 1.0, 1.0, 1.0, 0.9442854309054267, 0.1456878470421583]

def test_pwalk():
    a = iso.PRandomWalk([0, 2, 4, 5, 12], min=iso.PConstant(1), max=iso.PConstant(2))
    assert a.nextn(20) == [4, 0, 5, 0, 4, 5, 2, 4, 12, 5, 12, 4, 2, 5, 12, 4, 0, 12, 2, 4]

def test_pchoice():
    a = iso.PChoice(iso.PSequence([[ 0, 1, 2, 3], [ 4,5,6,7 ]]))
    assert a.nextn(20) == [3, 7, 0, 6, 3, 7, 2, 7, 2, 5, 1, 6, 1, 4, 2, 5, 2, 4, 0, 6]

def test_pchoice_weighted():
    a = iso.PChoice(iso.PSequence([[0, 1, 2, 3], [4, 5, 6, 7]]), iso.PSequence([[1, 0.5, 0.25, 0.1]]))
    assert a.nextn(20) == [2, 5, 0, 4, 0, 4, 1, 4, 0, 5, 2, 4, 0, 5, 1, 4, 2, 7, 1, 6]

def test_psample():
    p = iso.PSample(iso.PSequence([[1, 2, 3], [4, 5, 6]]), count=2)
    assert p.nextn(16) == [[2, 3], [4, 6], [3, 2], [5, 6], [2, 3], [6, 4], [3, 1], [5, 4], [1, 3], [6, 4], [2, 1], [6, 4], [3, 2], [5, 4], [2, 3], [5, 4]]

def test_psample_weighted():
    p = iso.PSample(iso.PSequence([[1, 2, 3], [4,5,6]]), count=2, weights=[0.5, 0.25, 0.1])
    assert p.nextn(16) == [[2, 1], [4, 5], [1, 2], [5, 4], [1, 2], [6, 4], [1, 3], [5, 4], [3, 2], [5, 6], [1, 3], [6, 5], [1, 2], [4, 5], [3, 2], [4, 6]]

def test_pshuffle():
    a = iso.PShuffle([ 1, 2, 3, 4, 5, 6], 3)
    assert list(a) == [2, 1, 3, 4, 6, 5, 4, 6, 1, 3, 2, 5, 6, 4, 2, 5, 3, 1, 6, 4, 2, 1, 5, 3]

def test_pshuffleevery():
    a = iso.PShuffleEvery(iso.PSeries(0, 1), 4)
    b = iso.PSubsequence(a, 0, 20)
    assert list(b) == [2, 0, 1, 3, 4, 5, 7, 6, 8, 10, 9, 11, 13, 12, 15, 14, 18, 16, 19, 17]

def test_pskip():
    a = iso.PSkip(iso.PSeries(0, 1), 0.5)
    assert a.nextn(20) == [None, None, 2, 3, None, 5, None, 7, 8, None, None, None, 12, None, None, 15, None, None, None, None]

def test_pskip_regular():
    a = iso.PSkip(iso.PSeries(0, 1), 0.5, True)
    assert a.nextn(20) == [None, 1, None, 3, None, 5, None, 7, None, 9, None, 11, None, 13, None, 15, None, 17, None, 19]

def test_pflipflop():
    a = iso.PFlipFlop(0, iso.PConstant(0.5), iso.PConstant(0.5))
    assert a.nextn(20) == [0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1]

def test_pswitchone():
    a = iso.PSwitchOne(iso.PSeries(0, 1), 4)
    assert a.nextn(20) == [0, 1, 2, 3, 0, 1, 3, 2, 0, 1, 2, 3, 3, 1, 2, 0, 3, 2, 1, 0]