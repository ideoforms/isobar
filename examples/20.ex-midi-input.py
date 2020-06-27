#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI input example
#------------------------------------------------------------------------

import isobar as iso
import logging
import time

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

midi_in = iso.MidiInputDevice()

notes = []
durations = []
last_note_time = None

print("Listening for notes on %s. Press Ctrl-C to stop." % midi_in.device_name)

try:
    while True:
        note = midi_in.receive()
        if note is not None:
            print(" - Read note: %s" % note.note)
            notes.append(note)
            if last_note_time is not None:
                durations.append(time.time() - last_note_time)
            last_note_time = time.time()

except KeyboardInterrupt:
    pass

if last_note_time:
    durations.append(time.time() - last_note_time)

    print()
    print("----------------------------------------------------")
    print("Ctrl-C detected, now playing back")
    print("----------------------------------------------------")

    timeline = iso.Timeline(60)
    timeline.stop_when_done = True
    timeline.schedule({
        "note": iso.PSequence([note.note for note in notes], 1),
        "duration": iso.PSequence(durations, 1)
    })
    timeline.run()
else:
    print()
    print("No notes detected")
