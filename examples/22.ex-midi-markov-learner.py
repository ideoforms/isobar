#!/usr/bin/env python3

#------------------------------------------------------------------------
# Parallel markov chain learner:
#
# 1. takes MIDI input, and constructs three markov chains for pitch, duration
#    and amplitude. 
# 2. after receiving a keyboard interrupt (ctrl-c), plays back melodies which are
#    statistically similar to the input.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io.midi import MidiIn, MidiOut

import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

import time

midi_in = MidiIn()
midi_out = MidiOut()

learner = iso.MarkovParallelLearners(3)
clock0 = time.time()

print("Awaiting MIDI clock signal...")

try:
    while True:
        note = midi_in.poll()
        if note is not None:
            clock = time.time()
            print("[%f] note %s (%d, %d)" % (clock, note, note.note, note.velocity))

            velocity = round(note.velocity, -1)
            dur = clock - clock0
            dur = round(dur, 2)

            learner.register([note.note, velocity, dur])
            clock0 = clock

except KeyboardInterrupt:
    pass

print("----------------------------------------------------")
print("Ctrl-C detected, now playing back")
print("----------------------------------------------------")

chains = learner.chains()

pitch = chains[0]
amp = chains[1]
dur = chains[2]

if len(pitch.nodes) == 0:
    print("No notes detected")
else:
    t = iso.Timeline(120, midi_out)
    t.sched({
        "note": pitch,
        "duration": dur,
        "amplitude": amp,
        "channel": 0
    })
    t.run()
