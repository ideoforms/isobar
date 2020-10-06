#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-write:
#
# Simple example of writing to a MIDI file in real time.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io import MidiFileOutputDevice

import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

key = iso.Key("C", "major")

filename = "output.mid"
output = MidiFileOutputDevice(filename)

timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=output)
timeline.stop_when_done = True

timeline.schedule({
    "note": iso.PDegree(iso.PSequence([ 0, 1, 2, 4 ], 4), key),
    "octave": 5,
    "gate": iso.PSequence([ 0.5, 1, 2, 1 ]),
    "amplitude": iso.PSequence([ 100, 80, 60, 40], 4),
    "duration": 1.0
})

timeline.schedule({
    "note": iso.PDegree(iso.PSequence([ 7, 6, 4, 2 ], 4), key),
    "octave": 6,
    "gate": 1,
    "amplitude": iso.PSequence([ 80, 70, 60, 50], 4),
    "duration": 1.0
}, delay=0.5)

timeline.run()
output.write()

print("Wrote to output file: %s" % filename)
