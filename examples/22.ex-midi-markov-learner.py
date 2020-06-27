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

import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

import time

midi_in = iso.MidiInputDevice()
midi_out = iso.MidiOutputDevice()

learner = iso.MarkovParallelLearners(3)
clock0 = time.time()

print("Listening for MIDI events...")

try:
    while True:
        message = midi_in.poll()
        if message is not None and message.type == "note_on":
            clock = time.time()
            print("[%f] %s (%d, %d)" % (clock, message, message.note, message.velocity))

            velocity = round(message.velocity, -1)
            dur = clock - clock0
            dur = round(dur, 2)

            learner.register([message.note, velocity, dur])
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
    timeline = iso.Timeline(120, midi_out)
    timeline.schedule({
        "note": pitch,
        "duration": dur,
        "amplitude": amp,
        "channel": 0
    })
    timeline.run()
