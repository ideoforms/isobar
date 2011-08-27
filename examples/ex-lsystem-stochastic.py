#!/usr/bin/python

# example-lsystem-stochastic:
# generates a stochastic l-system arpeggio

# import important things from isobar namespace.
from isobar import *
from isobar.io.midiout import *

import random
import time

notes = PLSys("N[+N--?N]+N[+?N]", depth = 4) 
notes = PDegree(notes, Scale.majorPenta)
notes = notes % 36 + 52

midi = MidiOut()

timeline = Timeline(120)
timeline.output(midi)

timeline.sched({ 'note': notes, 'dur': 0.25 })
timeline.run()
