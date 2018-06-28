#!/usr/bin/env python

from isobar import *

#------------------------------------------------------------------------
# walk up and down a minor scale
#------------------------------------------------------------------------
scale = Scale([ 0, 2, 3, 7, 9, 11 ])
degree = PBrown(0, 2, -8, 16, repeats = False)
notes = PDegree(degree, scale) + 60

#------------------------------------------------------------------------
# add a slight 4/4 emphasis and moderate variation in velocity
#------------------------------------------------------------------------
amp = PSeq([ 40, 30, 20, 25 ]) + PBrown(0, 2, -10, 10)

timeline = Timeline(170)
timeline.sched({ 'note': notes, 'dur': 0.25, 'gate': 0.9, 'amp' : amp })
timeline.run()
