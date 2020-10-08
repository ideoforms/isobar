import pytest
import isobar as iso
from . import dummy_timeline

def test_pglobals():
    with pytest.raises(KeyError):
        iso.Globals.get("key")

    iso.Globals.set("key", iso.Key("C", "major"))
    assert iso.Globals.get("key") == iso.Key("C", "major")

    pattern = iso.PGlobals("key")
    assert next(pattern) == iso.Key("C", "major")
    assert next(pattern) == iso.Key("C", "major")

def test_pstaticpattern(dummy_timeline):
    pattern = iso.PStaticPattern(pattern=iso.PSequence([1, 2, 3, 4], 1),
                                 element_duration=iso.PSequence([1, 2, 0, 1]))
    dummy_timeline.schedule({
        "note": pattern
    })
    dummy_timeline.stop_when_done = True
    dummy_timeline.run()
    event_times = [event[0] for event in dummy_timeline.output_device.events]
    event_notes = [event[2] for event in dummy_timeline.output_device.events]
    assert event_times == [0, 1, 1, 2, 2, 3, 3, 4]
    assert event_notes == [1, 1, 2, 2, 2, 2, 4, 4]

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
