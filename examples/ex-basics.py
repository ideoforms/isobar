#!/usr/bin/env python

#------------------------------------------------------------------------
# isobar: ex-basics
# 
# Example of some basic functionality: Pattern transformations,
# sequences, randomness, scheduling and parameter mapping.
#------------------------------------------------------------------------

from isobar import *
from isobar.io.midi import MidiOut

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

#------------------------------------------------------------------------
# Create a repeating sequence with scalar transposition:
# [ 36, 38, 43, 39, 36, 38, 43, 39, ... ]
#------------------------------------------------------------------------
a = PSeq([ 0, 2, 7, 3 ]) + 36

#------------------------------------------------------------------------
# Apply pattern-wise transposition
# [ 36, 50, 43, 51, ... ]
#------------------------------------------------------------------------
a = a + PSeq([ 0, 12, 24 ])

#------------------------------------------------------------------------
# Create a geometric chromatic series, repeated back and forth
#------------------------------------------------------------------------
b = PSeries(0, 2, 6) + 72
b = PPingPong(b)
b = PLoop(b)

#------------------------------------------------------------------------
# Create an velocity series, with emphasis every 4th note,
# plus a random walk to create gradual dynamic changes
#------------------------------------------------------------------------
amp = PSeq([ 50, 35, 25, 35 ]) + PBrown(0, 1, -20, 20)

#------------------------------------------------------------------------
# A Timeline schedules events at a given BPM.
# by default, send these over the first MIDI output.
#------------------------------------------------------------------------
output = MidiOut()
timeline = Timeline(120, output)

#------------------------------------------------------------------------
# Schedule events, with properties mapped to the Pattern objects.
#------------------------------------------------------------------------
timeline.sched({ 'note': a, 'dur': 1, 'gate': 2 })
timeline.sched({ 'note': b, 'dur': 0.25, 'amp': amp })

timeline.run()
