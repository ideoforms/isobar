#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-write:
#
# Simple example of writing to a MIDI file in real time.
#------------------------------------------------------------------------

from isobar import *
import logging

def main():
    key = Key("C", "major")

    filename = "output.mid"
    output = MidiFileOutputDevice(filename)

    timeline = Timeline(MAX_CLOCK_RATE, output_device=output)
    timeline.stop_when_done = True

    timeline.schedule({
        "note": PDegree(PSequence([0, 1, 2, 4], 4), key),
        "octave": 5,
        "gate": PSequence([0.5, 1, 2, 1]),
        "amplitude": PSequence([100, 80, 60, 40], 4),
        "duration": 1.0
    })

    timeline.schedule({
        "note": PDegree(PSequence([7, 6, 4, 2], 4), key),
        "octave": 6,
        "gate": 1,
        "amplitude": PSequence([80, 70, 60, 50], 4),
        "duration": 1.0
    }, delay=0.5)

    timeline.run()
    output.write()

    print("Wrote to output file: %s" % filename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
