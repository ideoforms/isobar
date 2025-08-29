#!/usr/bin/env python3

#------------------------------------------------------------------------
# Link clock example.
#
# Uses the Link network clock provided by Ableton Live to implement
# tempo and beat synchronisation between multiple processes.
#
# To test this example:
#  - start Ableton Live, with a MIDI instrument listening for events
#  - enable the Link icon in the top left
#  - run two or more instances of this script simultaneously
# 
# The timelines will automatically synchronise, and track the same BPM
# if the tempo is changed in Live (or by any of the client processes).
#
# Thanks to Raphaël Forment for providing LinkPython-extern.
#------------------------------------------------------------------------

from isobar import *
import logging

def main():
    timeline = Timeline(120)
    timeline.clock_source = AbletonLinkClock()
    timeline.schedule({
        "key": Key("C", "minorPenta"),
        "octave": random.choice([4, 5, 6]),
        "degree": PLoop(PSubsequence(PWhite(0, 12),
                               0, 8)),
        "duration": PLoop(PSubsequence(PChoice([0.25, 0.5, 1.0], [1, 0.5, 0.25]),
                                 0, 6))
    }, quantize=None)
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
