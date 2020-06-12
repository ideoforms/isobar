#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-write:
#
# Simple example of writing to a MIDI file in real time.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io import MidiFileOut

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

key = iso.Key("C", "major")

filename = "output.mid"
output = MidiFileOut(filename)

timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=output)
timeline.sched({
    iso.EVENT_NOTE: iso.PDegree(iso.PSequence([ 0, 1, 2, 4 ], 4), key),
    iso.EVENT_OCTAVE: 5,
    iso.EVENT_GATE: iso.PSequence([ 0.5, 1, 2, 1 ]),
    iso.EVENT_AMPLITUDE: iso.PSequence([ 100, 80, 60, 40], 4),
    iso.EVENT_DURATION: 1.0
})
timeline.sched({
    iso.EVENT_NOTE: iso.PDegree(iso.PSequence([ 7, 6, 4, 2 ], 4), key),
    iso.EVENT_OCTAVE: 6,
    iso.EVENT_GATE: 1,
    iso.EVENT_AMPLITUDE: iso.PSequence([ 80, 70, 60, 50], 4),
    iso.EVENT_DURATION: 1.0
}, delay=0.5)
timeline.run()
output.write()

print("Wrote to output file: %s" % filename)
