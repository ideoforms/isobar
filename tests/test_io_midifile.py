""" Unit tests for Key """

import isobar as iso
from isobar.io.midifile import MidiFileOut, MidiFileIn
import pytest
from . import dummy_timeline

def test_io_midifile_write(dummy_timeline):
    events = {
        iso.EVENT_NOTE: iso.PSequence([60, 62, 64, 67], 1),
        iso.EVENT_DURATION: iso.PSequence([0.5, 1.5, 1, 1], 1),
        iso.EVENT_GATE: iso.PSequence([2, 0.5, 1, 1], 1),
        iso.EVENT_AMPLITUDE: iso.PSequence([64, 32, 16, 8], 1)
    }

    midifile = MidiFileOut("output.mid")
    dummy_timeline.stop_when_done = True
    dummy_timeline.output_device = midifile
    dummy_timeline.schedule(events)
    dummy_timeline.run()
    midifile.write()

    d = MidiFileIn("output.mid").read()

    for key in events.keys():
        assert isinstance(d[key], iso.PSequence)
        assert list(d[key]) == list(events[key])
