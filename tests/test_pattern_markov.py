import isobar as iso

def test_pmarkov():
    a = iso.PMarkov([ 1, 1, 2, 3, 1 ])
    a.seed(0)
    assert a.nextn(16) == [2, 3, 1, 2, 3, 1, 2, 3, 1, 1, 1, 2, 3, 1, 2, 3]

    a = iso.PMarkov({ 1 : [ 2, 2, 3 ], 2 : [ 3 ], 3 : [ 1, 2 ] })
    a.seed(0)
    assert a.nextn(16) == [2, 3, 1, 2, 3, 2, 3, 2, 3, 1, 3, 1, 2, 3, 1, 3]