#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-subsequence
#------------------------------------------------------------------------

from isobar_ext import *

import logging

def main():
    scale = Scale.pelog
    degree = PBrown(0, 3, -12, 12)
    sequence = PDegree(degree, scale)

    offset = PStutter(PWhite(0, 16), 4)
    sequence = PSubsequence(sequence, offset, 4)
    sequence = PPermut(sequence)
    sequence = PReset(sequence, PImpulse(12))

    amp = PSequence([45, 35, 25, 40]) + PBrown(0, 1, -20, 20)

    gate = PBrown(1.5, 0.01, 0.6, 2.5)

    timeline = Timeline(120)
    timeline.schedule({
        "note": sequence,
        "amplitude": amp.copy(),
        "duration": 0.25,
        "gate": gate.copy(),
        "transpose": 60
    })
    timeline.schedule({
        "note": sequence.copy() + 24,
        "amplitude": amp.copy(),
        "duration": 0.5,
        "gate": gate.copy(),
        "transpose": 60
    })
    timeline.schedule({
        "note": sequence.copy() - 24,
        "amplitude": 10 + amp.copy() * 0.5,
        "duration": PChoice([4, 4, 6, 8]),
        "gate": gate.copy(),
        "transpose": 60
    })

    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
