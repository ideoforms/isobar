#!/usr/bin/python

# parallel markov chain learner:
# 1. takes MIDI input, and constructs three markov chains for pitch, duration
#    and amplitude. 
# 2. after receiving a low "C", plays back melodies which are statistically
#    similar to the input.
# after francois pachet's "continuator".

from isobar import *
from isobar.io.midi import *

import time

m_in  = MidiIn()
m_out = MidiOut()

learner = MarkovLParallel(3)
clock0 = 0

while True:
    note = m_in.poll()
    if note is not None:
        clock = time.clock()
        print "[%f] note %s (%d, %d)" % (clock, note, note.midinote, note.velocity)
        if note.midinote == 36:
            break

        dur = clock - clock0
        dur = round(dur, 2)

        learner.register([ note.midinote, round(note.velocity, -1), dur ])
        clock0 = clock

print "----------------------------------------------------"
print "EOF detected, now playing back"
print "----------------------------------------------------"

chains = learner.chains()
pitch = PMarkov(chains[0])
amp   = PMarkov(chains[1])
dur   = PMarkov(chains[2])

t = Timeline(120, m_out)
print " - nodes: %s" % p.markov.nodes
print " - edges: %s" % p.markov.edges
t.sched({ 'note': pitch, 'dur': dur, 'amp': amp, 'channel': 0 })
t.run()

