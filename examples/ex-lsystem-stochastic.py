#!/usr/bin/env python

#------------------------------------------------------------------------
# isobar: ex-lsystem-stochastic
#
# Generates a stochastic L-system arpeggio
#------------------------------------------------------------------------

from isobar import *
from isobar.io.midi import *

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

import random
import time

notes = PLSys("N[+N--?N]+N[+?N]", depth=4) 
notes = PDegree(notes, Scale.majorPenta)
notes = notes % 36 + 52

midi = MidiOut()

timeline = Timeline(120)
timeline.add_output(midi)

timeline.sched({ 'note': notes, 'dur': 0.1 })
timeline.run()
