#!/usr/bin/python

from isobar import *
from isobar.io.midiout import *

scale = Scale([ 0, 2, 3, 7, 9, 11 ])
degree = PBrown(0, 2, -8, 8, repeats = False)

notes = PDegree(degree, scale) + 60

midi = MidiOut()
timeline = Timeline(160)
timeline.output(midi)

timeline.sched({ 'note': notes, 'dur': 0.25, 'gate': 0.9 })

timeline.run()
