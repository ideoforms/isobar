""" Unit tests for isobar """

import isobar as iso
import pytest
from isobar.io import DummyOutputDevice

def test_timeline():
    timeline = iso.Timeline(120)
    timeline.run()

def test_timeline_schedule():
    dummy = DummyOutputDevice()
    timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=dummy)
    timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    })
    timeline.run()
    assert len(dummy.events) == 2
    assert dummy.events[0] == [pytest.approx(0.0), "note_on", 1, 64, 0]
    assert dummy.events[1] == [pytest.approx(1.0), "note_off", 1, 0]