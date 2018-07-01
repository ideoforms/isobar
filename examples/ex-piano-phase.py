#!/usr/bin/env python

#------------------------------------------------------------------------
# Implementation of Steve Reich's "Piano Phase" (1967):
# Two identical piano lines, one with a slightly longer duration,
# moving in and out of phase with one another.
#------------------------------------------------------------------------

# by default, writes to the current MIDI output.
from isobar import *

import logging
logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] %(message)s")

# melody line
seq = PSeq([ -7, -5, 0, 2, 3, -5, -7, 2, 0, -5, 3, 2 ])

# create a timeline at 160BPM
timeline = Timeline(160)

# schedule two identical melodies.
# we must copy the note sequence or else the position will be stepped
# by two every note... try removing the .copy() and see what happens!
timeline.sched({ 'note': seq.copy() + 60, 'dur': 0.5 })
timeline.sched({ 'note': seq.copy() + 72, 'dur': 0.5 * 1.01 })

# start playing, and block forever.
# alternatively, use timeline.background() to retain foreground control.
timeline.run()
