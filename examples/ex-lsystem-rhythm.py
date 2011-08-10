#!/usr/bin/python

# test-plsys-rhythm:
# generates a rhythm line based on an l-system sprouting structure,
# output over MIDI.

# import important things from isobar namespace.
from isobar import *
from isobar.io.midiout import *

import random
import time

# generate a set of pitches based on an l-system, with recursive depth 4.
# symbols:
#  N = generate note node
#  + = transpose up one semitone
#  - = transpose down one semitone
#  [ = enter recursive branch
#  ] = leave recursive branch
notes = PLSys("N+[+N+N--N+N]+N[++N]", depth = 4)
notes = PDegree(notes, Scale.chromatic)

# use another l-system to generate time intervals.
# take absolute values so that intervals are always positive.
times = PLSys("[N+[NN]-N+N]+N-N+N", depth = 3)
times = PAbs(PDiff(times))
delay = PDelay(notes, times)

# ...and another l-system for amplitudes.
velocity = (PLSys("N+N[++N+N--N]-N[--N+N]") + PWhite(-4, 4)) * 8
velocity = PAbs(velocity)

m = MidiOut()

# handle our own timing based on these patterns.
while True:
	note = delay.next()
	if note is not None:
		print note
		vel = velocity.next()
		m.noteOn(note, vel)
		m.noteOff(note)
	else:
		print "-"
	time.sleep(0.2)
