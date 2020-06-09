""" Unit tests for Track """

import isobar as iso
import pytest
from isobar.io import DummyOutputDevice

def test_track():
    dummy = DummyOutputDevice()
    track = iso.Track({ iso.EVENT_NOTE: iso.PSequence([], 0) }, output_device=dummy)
    track.tick(1 / iso.TICKS_PER_BEAT)
    assert track.is_finished