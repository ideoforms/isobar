import pytest
import isobar as iso
from . import dummy_timeline

def test_pglobals():
    pass

def test_pstaticpattern():
    pass

def test_pcurrenttime(dummy_timeline):
    pattern = iso.PCurrentTime()
    assert next(pattern) == 0

    values = []
    def action(t):
        nonlocal values
        values.append(t)

    dummy_timeline.schedule({
        "action": action,
        "args": {
            "t": iso.PCurrentTime()
        }
    })

    dummy_timeline.tick()
    assert values == [0.0]
    for n in range(dummy_timeline.ticks_per_beat - 1):
        dummy_timeline.tick()
    assert values == [0.0]
    dummy_timeline.tick()
    assert values == [0.0, 1.0]
