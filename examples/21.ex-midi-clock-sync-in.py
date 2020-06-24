#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI clock sync input example.
# Start an external MIDI clock with this device as the clock target.
# The MidiIn object estimates the input tempo via a moving average.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io.midi import MidiIn

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

midi_in = MidiIn()

print("Start a MIDI clock device with %s as the clock destination" % midi_in.device_name)
print("Awaiting clock signal...")

def print_tempo():
    if midi_in.tempo:
        print("Estimated tempo: %.3f" % midi_in.tempo)

timeline = iso.Timeline(120, clock_source=midi_in)
timeline.schedule({
    "action": print_tempo
})
timeline.run()
