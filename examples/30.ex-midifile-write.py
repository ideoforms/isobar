#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-write:
#
# Simple example of writing to a MIDI file in real time.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io import MidiFileOut

import logging

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

chords = iso.PSequence([ [0, 2, 4], [1, 3, 5], [2, 4, 6], [3, 5, 7], [4, 6, 8] ], 1)
chords = iso.PSequence([0, 1, 2, 3], 1)

filename = "output.mid"
output = MidiFileOut(filename)

timeline = iso.Timeline(120, output)
timeline.sched({
    iso.EVENT_NOTE: chords,
    iso.EVENT_DURATION: 0.25,
    iso.EVENT_GATE: 1.0
})
timeline.run()
output.write()

print("Wrote to output file: %s" % filename)
