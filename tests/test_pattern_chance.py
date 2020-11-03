import pytest
import isobar as iso

@pytest.fixture(autouse=True)
def test_seed_random():
    iso.random_seed(0)

def test_pwhite():
    a = iso.PWhite(iso.PConstant(5), iso.PConstant(10))
    a.seed(0)
    assert a.nextn(10) == [9, 8, 7, 6, 7, 7, 8, 6, 7, 7]

    a = iso.PWhite(iso.PConstant(-1.0), iso.PConstant(1.0))
    a.seed(0)
    assert a.nextn(10) == [0.6888437030500962, 0.515908805880605, -0.15885683833831, -0.4821664994140733, 0.02254944273721704, -0.19013172509917142, 0.5675971780695452, -0.3933745478421451, -0.04680609169528838, 0.1667640789100624]

def test_pbrown():
    a = iso.PBrown(0, iso.PConstant(5), iso.PConstant(-5), iso.PConstant(5))
    a.seed(0)
    expected = [0, 1, 2, -3, -4, -1, 1, 2, 1, 3, 3, 5, 3, 5, 2, 1, -2, -5, -1, -2]
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

    a = iso.PBrown(0.0, 1.0, -1.0, 1.0)
    a.seed(0)
    expected = [0.0, 0.6888437030500962, 1.0, 0.84114316166169, 0.3589766622476167, 0.38152610498483375, 0.19139437988566232, 0.7589915579552076, 0.36561701011306247, 0.3188109184177741]
    assert a.nextn(10) == expected
    a.reset()
    assert a.nextn(10) == expected

def test_pcoin():
    a = iso.PCoin(0.75)
    a.seed(0)
    assert a.nextn(16) == [0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1]
    a.seed(0)
    assert a.nextn(16) == [0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1]

def test_pwalk():
    a = iso.PRandomWalk([0, 2, 4, 5, 12], min=iso.PConstant(1), max=iso.PConstant(2))
    expected = [4, 0, 5, 0, 4, 5, 2, 4, 12, 5, 12, 4, 2, 5, 12, 4, 0, 12, 2, 4]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pchoice():
    a = iso.PChoice(iso.PSequence([[0, 1, 2, 3], [4, 5, 6, 7]]))
    a.seed(0)
    expected = [3, 7, 0, 6, 3, 7, 2, 7, 2, 5, 1, 6, 1, 4, 2, 5, 2, 4, 0, 6]
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pchoice_weighted():
    a = iso.PChoice(iso.PSequence([[0, 1, 2, 3], [4, 5, 6, 7]]), iso.PSequence([[1, 0.5, 0.25, 0.1]]))
    a.seed(0)
    expected = [2, 5, 0, 4, 0, 4, 1, 4, 0, 5, 2, 4, 0, 5, 1, 4, 2, 7, 1, 6]
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_psample():
    a = iso.PSample(iso.PSequence([[1, 2, 3], [4, 5, 6]]), count=2)
    expected = [[2, 3], [4, 6], [3, 2], [5, 6], [2, 3], [6, 4], [3, 1], [5, 4], [1, 3], [6, 4], [2, 1], [6, 4], [3, 2], [5, 4], [2, 3], [5, 4]]
    a.seed(0)
    assert a.nextn(16) == expected
    a.reset()
    assert a.nextn(16) == expected

def test_psample_weighted():
    a = iso.PSample(iso.PSequence([[1, 2, 3], [4, 5, 6]]), count=2, weights=[0.5, 0.25, 0.1])
    expected = [[2, 1], [4, 5], [1, 2], [5, 4], [1, 2], [6, 4], [1, 3], [5, 4], [3, 2], [5, 6], [1, 3], [6, 5], [1, 2], [4, 5], [3, 2], [4, 6]]
    a.seed(0)
    assert a.nextn(16) == expected
    a.reset()
    assert a.nextn(16) == expected

def test_pshuffle():
    a = iso.PShuffle([1, 2, 3, 4, 5, 6], 2)
    expected = [5, 3, 2, 1, 6, 4, 5, 3, 2, 1, 6, 4]
    a.seed(0)
    assert list(a) == expected
    a.reset()
    assert list(a) == expected

def test_pshuffleevery():
    a = iso.PShuffleInput(iso.PSeries(0, 1), 4)
    expected = [2, 0, 1, 3, 4, 5, 7, 6, 8, 10, 9, 11, 13, 12, 15, 14, 18, 16, 19, 17]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pskip():
    a = iso.PSkip(iso.PSeries(0, 1), 0.5)
    expected = [None, None, 2, 3, None, 5, None, 7, 8, None, None, None, 12, None, None, 15, None, None, None, None]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pskip_regular():
    a = iso.PSkip(iso.PSeries(0, 1), 0.5, True)
    expected = [None, 1, None, 3, None, 5, None, 7, None, 9, None, 11, None, 13, None, 15, None, 17, None, 19]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pflipflop():
    a = iso.PFlipFlop(0, iso.PConstant(0.5), iso.PConstant(0.5))
    expected = [0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

def test_pswitchone():
    a = iso.PSwitchOne(iso.PSeries(0, 1), 4)
    expected = [0, 1, 2, 3, 0, 1, 3, 2, 0, 1, 2, 3, 3, 1, 2, 0, 3, 2, 1, 0]
    a.seed(0)
    assert a.nextn(20) == expected
    a.reset()
    assert a.nextn(20) == expected

