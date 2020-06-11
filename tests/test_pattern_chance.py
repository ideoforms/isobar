import pytest
import isobar as iso

@pytest.fixture(autouse=True)
def test_seed_random():
    iso.random_seed(0)

def test_pwhite():
    a = iso.PWhite(5, 10)
    assert a.nextn(10) == [8, 8, 5, 7, 9, 8, 8, 7, 8, 7]

def test_pbrown():
    pass

def test_pwalk():
    pass

def test_pchoice():
    pass

def test_pwchoice():
    pass

def test_pshuffle():
    pass

def test_pshuffleevery():
    pass

def test_pselfindex():
    pass

def test_pskip():
    pass

def test_pflipflop():
    pass

def test_pswitchone():
    pass