#!/usr/bin/env python

# example-lsystem-stochastic:
# generates a stochastic l-system arpeggio

# import important things from isobar namespace.
from isobar import *
from isobar.io.midi import *

import logging
logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] %(message)s")

import random
import time

notes = PLSys("N[+N--?N]+N[+?N]", depth = 4) 
notes = PDegree(notes, Scale.majorPenta)
notes = notes % 36 + 52

midi = MidiOut()

timeline = Timeline(120)
timeline.add_output(midi)

timeline.sched({ 'note': notes, 'dur': 0.25 })
timeline.run()
