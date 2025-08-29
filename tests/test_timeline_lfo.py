""" Unit tests for LFO """

import pytest
import isobar as iso
from . import dummy_timeline

@pytest.mark.skip
def test_lfo(dummy_timeline):
    lfo = iso.LFO(dummy_timeline, "sine", 1.0)
    assert lfo.value == 0.5
    for n in range(dummy_timeline.ticks_per_beat):
        lfo.tick()
    assert lfo.value == 0.5