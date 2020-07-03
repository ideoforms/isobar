import isobar as iso

def test_plsystem():
    a = iso.PLSystem("N[-N++N]-N", 1)
    assert list(a) == [0, -1, 1, -1]

    a = iso.PLSystem("N[-N++N]-N", 2)
    assert list(a) == [0, -1, 1, -1, -2, -3, -1, -3, -1, -2, 0, -2, -2, -3, -1, -3]
