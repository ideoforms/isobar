#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-walk
#
# Brownian walk around a scale.
#------------------------------------------------------------------------

from isobar_ext import *

import logging

def main():
    #------------------------------------------------------------------------
    # walk up and down a minor scale
    #------------------------------------------------------------------------
    scale = Scale([0, 2, 3, 7, 9, 11])
    degree = PBrown(0, 2, -8, 16)
    notes = PDegree(degree, scale) + 60

    #------------------------------------------------------------------------
    # add a slight 4/4 emphasis and moderate variation in velocity
    #------------------------------------------------------------------------
    amp = PSequence([40, 30, 20, 25]) + PBrown(0, 2, -10, 10)

    timeline = Timeline(170)
    timeline.schedule({
        "note": notes,
        "duration": 0.25,
        "gate": 0.9,
        "amplitude": amp})
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
