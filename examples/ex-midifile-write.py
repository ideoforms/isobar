#!/usr/bin/env python

#------------------------------------------------------------------------
# ex-midifile-write:
# Simple example of writing to a MIDI file in real time.
#------------------------------------------------------------------------

from isobar import *
from isobar.io.midifile import MidiFileOut

import logging
logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] %(message)s")

filename = "output.mid"
output = MidiFileOut(filename)

timeline = Timeline(120, output)
timeline.sched({ 'note' : [ 60, 64, 67, 72 ], 'dur' : 0.25 })
timeline.run()

output.write()

print("Wrote to output file: %s" % filename)
