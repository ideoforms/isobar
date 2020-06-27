#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI clock sync input example.
# Start an external MIDI clock with this device as the clock target.
# The MidiInputDevice object estimates the input tempo via a moving average.
#------------------------------------------------------------------------

import isobar as iso

midi_in = iso.MidiInputDevice()

def print_tempo():
    if midi_in.tempo:
        print("Estimated tempo: %.3f" % midi_in.tempo)

timeline = iso.Timeline(120, clock_source=midi_in)
timeline.schedule({
    "action": print_tempo
})

print("Awaiting MIDI clock signal from %s..." % midi_in.device_name)

timeline.run()
