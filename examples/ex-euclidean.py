#!/usr/bin/python

#------------------------------------------------------------------------
# Simple example of three parallel voices based on the Euclidean
# rhythm.
#------------------------------------------------------------------------

from isobar import *

timeline = Timeline(120, debug = True)

timeline.sched({ 'note' : 60 * PEuclidean(5, 8), 'dur' : 0.5 })
timeline.sched({ 'note' : 62 * PEuclidean(5, 13), 'dur' : 0.25 })
timeline.sched({ 'note' : 64 * PEuclidean(7, 15), 'dur' : 0.5 })

timeline.run()

