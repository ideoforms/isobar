#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI input example
#------------------------------------------------------------------------

import isobar as iso
from isobar.io.midi import MidiIn, MidiOut

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

import time

midi_in = MidiIn()
midi_out = MidiOut()

learner = iso.MarkovParallelLearners(3)
clock0 = 0

print("Awaiting MIDI clock signal...")

try:
    while True:
        note = midi_in.poll()
        if note is not None:
            clock = time.clock()
            print("[%f] note %s (%d, %d)" % (clock, note, note.midinote, note.velocity))

            velocity = round(note.velocity, -1)
            dur = clock - clock0
            dur = round(dur, 2)

            learner.register([note.midinote, velocity, dur])
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
        iso.EVENT_NOTE: pitch,
        iso.EVENT_DURATION: dur,
        iso.EVENT_AMPLITUDE: amp,
        iso.EVENT_CHANNEL: 0
    })
    t.run()
