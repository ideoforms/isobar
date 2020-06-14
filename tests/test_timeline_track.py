""" Unit tests for Track """

import isobar as iso
import pytest
from . import dummy_timeline

@pytest.fixture()
def dummy_track():
    return iso.Track(output_device=iso.io.DummyOutputDevice())

def test_track(dummy_timeline):
    track = iso.Track({
        iso.EVENT_NOTE: iso.PSequence([], 0)
    }, timeline=dummy_timeline)
    track.tick()
    assert track.is_finished