#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI input example
#------------------------------------------------------------------------

import isobar as iso
from isobar.io.midi import MidiIn

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

midi_in = MidiIn()
notes = []

try:
    while True:
        note = midi_in.receive()
        if note is not None:
            print("Received note: %s" % note.note)
            notes.append(note)

except KeyboardInterrupt:
    pass

print()
print("----------------------------------------------------")
print("Ctrl-C detected, now playing back")
print("----------------------------------------------------")

t = iso.Timeline(120)
t.sched({
    "note": iso.PSequence([ note.note for note in notes ], 1),
    "duration": 0.5
})
t.run()
