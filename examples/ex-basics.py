#!/usr/bin/python

from isobar import *

# create a repeating sequence with scalar transposition:
# [ 48, 50, 57, 60 ] ...
seqA = PSeq([ 0, 2, 7, 3 ]) + 36

# apply pattern-wise transposition
# [ 48, 62, 57, 72 ] ...
seqA = seqA + PSeq([ 0, 12 ])

# create a geometric chromatic series, repeated back and forth
seqB = PSeries(0, 1, 12) + 72
seqB = PPingPong(seqB)

# create an velocity series, with emphasis every 4th note,
# plus a random walk to create gradual dynamic changes
amp = PSeq([ 50, 35, 25, 35 ]) + PBrown(0, 1, -20, 20)

# a Timeline schedules events at a given BPM, sent over a specified output
timeline = Timeline(120)

# assign each of our Patterns to particular properties
timeline.sched({ 'note': seqA, 'dur': 1, 'gate': 2 })
timeline.sched({ 'note': seqB, 'dur': 0.25, 'amp': amp })

timeline.run()
