#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-permutations
# 
# PPermut generates every possible permutation of a sequence:
# [1, 2, 3] -> [1, 2, 3, 1, 3, 2, 2, 1, 3, 2, 3, 1, 3, 1, 2, 3, 2, 1]
#
# Use simple permutations to generate intertwining musical structures.
#------------------------------------------------------------------------

from isobar_ext import *
import random
import logging

def main():
    #------------------------------------------------------------------------
    # Create a pitch line comprised of multiple permutations on
    # a pentatonic scale
    #------------------------------------------------------------------------
    ppitch = PShuffle([random.randint(-6, 6) for _ in range(6)])
    ppitch = PPermut(ppitch)
    ppitch = PDegree(ppitch, Key("C", "majorPenta"))

    #------------------------------------------------------------------------
    # Create permuted sets of durations and amplitudes.
    # Different lengths mean poly-combinations.
    #------------------------------------------------------------------------
    pdur = PShuffle([1, 1, 2, 2, 4], 1)
    pdur = PPermut(pdur) / 4

    pamp = PShuffle([10, 15, 20, 35], 2)
    pamp = PPermut(pamp)

    #------------------------------------------------------------------------
    # Schedule on a 60bpm timeline and send to MIDI output
    #------------------------------------------------------------------------
    timeline = Timeline(60)
    timeline.schedule({
        "note": ppitch + 60,
        "duration": pdur,
        "amplitude": pamp,
        "channel": 0
    })
    timeline.schedule({
        "note": ppitch + 24,
        "duration": pdur * 4,
        "amplitude": pamp,
        "channel": 1,
        "gate": 2
    })
    timeline.schedule({
        "note": ppitch + 72,
        "duration": pdur / 2,
        "channel": 1,
        "gate": 1,
        "amplitude": pamp / 2
    })

    #------------------------------------------------------------------------
    # Begin playback
    #------------------------------------------------------------------------
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
