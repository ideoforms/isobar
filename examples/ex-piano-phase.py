#!/usr/bin/env python

#------------------------------------------------------------------------
# isobar: ex-piano-phase
# 
# Implementation of Steve Reich's "Piano Phase" (1967):
# Two identical piano lines, one with a slightly longer duration,
# moving in and out of phase with one another.
#------------------------------------------------------------------------

from isobar import *

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

#------------------------------------------------------------------------
# Melody line
#------------------------------------------------------------------------
seq = PSeq([ -7, -5, 0, 2, 3, -5, -7, 2, 0, -5, 3, 2 ])

#------------------------------------------------------------------------
# Create a timeline at 160BPM
#------------------------------------------------------------------------
timeline = Timeline(160)

#------------------------------------------------------------------------
# Schedule two identical melodies.
# We must copy the note sequence or else the position will be stepped
# by two every note... try removing the .copy() and see what happens!
#------------------------------------------------------------------------
timeline.sched({ 'note': seq.copy() + 60, 'dur': 0.5 })
timeline.sched({ 'note': seq.copy() + 72, 'dur': 0.5 * 1.01 })

#------------------------------------------------------------------------
# Start playing via default MIDI out, and block forever.
# Alternatively, use timeline.background() to retain foreground control.
#------------------------------------------------------------------------
timeline.run()
