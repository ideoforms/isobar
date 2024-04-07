#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-lsystem-stochastic
#
# Generates a stochastic L-system arpeggio
#------------------------------------------------------------------------

from isobar_ext import *

import logging

def main():
    notes = PLSystem("N[+N--?N]+N[+?N]", depth=4)
    notes = PDegree(notes, Scale.majorPenta)
    notes = notes % 36

    timeline = Timeline(180)

    timeline.schedule({
        "note": notes,
        "duration": 0.25,
        "transpose": 50
    })
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()