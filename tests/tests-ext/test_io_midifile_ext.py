""" Unit tests for Key """

import os
import isobar_ext as iso
from isobar_ext.io.midifile import MidiFileOutputDevice, MidiFileInputDevice
import pytest
from tests import dummy_timeline


def test_io_midifile_write_rests(dummy_timeline):
    events = {
        iso.EVENT_NOTE: iso.PSequence([60, None, 55, None], 1),
        iso.EVENT_DURATION: iso.PSequence([0.5, 1.5, 1, 1], 1),
        iso.EVENT_GATE: iso.PSequence([2, 0.5, 1, 1], 1),
        iso.EVENT_AMPLITUDE: iso.PSequence([64, 32, 16, 8], 1)
    }

    midifile = MidiFileOutputDevice("output.mid")
    dummy_timeline.output_device = midifile
    dummy_timeline.schedule(events)
    dummy_timeline.run()
    midifile.write()

    d = MidiFileInputDevice("output.mid").read()

    for key in events.keys():
        assert isinstance(d[key], iso.PSequence)
        if key == iso.EVENT_NOTE:
            assert list(d[key]) == [e or 0 for e in list(events[key])]
        elif key == iso.EVENT_DURATION:
            assert pytest.approx(list(d[key]), rel=0.01) == list(events[key])
        elif key == iso.EVENT_GATE:
            assert pytest.approx(list(d[key]), rel=0.3) == list(events[key])
        elif key == iso.EVENT_AMPLITUDE:
            amp = [am if nt else 0 for (am, nt) in zip(events[key].sequence, events[iso.EVENT_NOTE].sequence)]
            assert list(d[key]) == amp
        else:
            assert list(d[key]) == list(events[key])

    os.unlink("output.mid")

