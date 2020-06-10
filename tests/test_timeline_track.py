""" Unit tests for Track """

import isobar as iso
import pytest

@pytest.fixture()
def dummy_track():
    return iso.Track(output_device=iso.io.DummyOutputDevice())

def test_track():
    dummy = iso.io.DummyOutputDevice()
    track = iso.Track({iso.EVENT_NOTE: iso.PSequence([], 0)}, output_device=dummy)
    track.tick(1 / iso.TICKS_PER_BEAT)
    assert track.is_finished