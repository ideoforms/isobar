#!/usr/bin/env python

#------------------------------------------------------------------------
# Parallel markov chain learner:
# 1. takes MIDI input, and constructs three markov chains for pitch, duration
#    and amplitude. 
# 2. after receiving a keyboard interrupt (ctrl-c), plays back melodies which are
#    statistically similar to the input.
#------------------------------------------------------------------------

from isobar import *
from isobar.io.midi import *

import logging
logging.basicConfig(level = logging.INFO, format = "[%(asctime)s] %(message)s")

import time

m_in  = MidiIn()
m_out = MidiOut()

learner = MarkovParallelLearners(3)
clock0 = 0

print("Awaiting MIDI clock signal...")

try:
    while True:
        note = m_in.poll()
        if note is not None:
            clock = time.clock()
            print("[%f] note %s (%d, %d)" % (clock, note, note.midinote, note.velocity))

            dur = clock - clock0
            dur = round(dur, 2)

            learner.register([ note.midinote, round(note.velocity, -1), dur ])
            clock0 = clock

except KeyboardInterrupt:
    pass

print("----------------------------------------------------")
print("Ctrl-C detected, now playing back")
print("----------------------------------------------------")

chains = learner.chains()

pitch = chains[0]
amp   = chains[1]
dur   = chains[2]

if len(pitch.nodes) == 0:
    print("No notes detected")
else:
    t = Timeline(120, m_out)
    t.sched({ 'note': pitch, 'dur': dur, 'amp': amp, 'channel': 0 })
    t.run()

