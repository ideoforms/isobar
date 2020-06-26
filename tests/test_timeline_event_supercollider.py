""" Unit tests for events """

import isobar as iso
import pytest
from . import dummy_timeline

class DummySuperColliderOutputDevice(iso.OutputDevice):
    def __init__(self):
        self.events = []

    def create(self, name, params):
        self.events.append([name, params])

def test_event_supercollider(dummy_timeline):
    output_device = DummySuperColliderOutputDevice()
    dummy_timeline.output_device = output_device
    dummy_timeline.schedule({
        iso.EVENT_SUPERCOLLIDER_SYNTH: iso.PSequence([ "foo", "bar" ]),
        iso.EVENT_SUPERCOLLIDER_SYNTH_PARAMS: {
            "buffer": iso.PSequence([1, 2]),
            "rate": iso.PSequence([0.5, 1, 2], 1)
        }
    })
    dummy_timeline.run()
    assert output_device.events == [
        ["foo", {"buffer": 1, "rate": 0.5}],
        ["bar", {"buffer": 2, "rate": 1}],
        ["foo", {"buffer": 1, "rate": 2}],
    ]
