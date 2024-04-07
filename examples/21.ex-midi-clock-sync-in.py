#!/usr/bin/env python3

#------------------------------------------------------------------------
# MIDI clock sync input example.
# Start an external MIDI clock with this device as the clock target.
# The MidiInputDevice object estimates the input tempo via a moving average.
#------------------------------------------------------------------------

from isobar_ext import *

def main():
    midi_in = MidiInputDevice()

    def print_tempo():
        if midi_in.tempo:
            print("Estimated tempo: %.3f" % midi_in.tempo)

    timeline = Timeline(120, clock_source=midi_in)
    timeline.schedule({
        "action": print_tempo
    })

    print("Awaiting MIDI clock signal from %s..." % midi_in.device_name)

    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
