#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-euclidean
#
# Uses Euclidean rhythms to generate multiple polyrhythmic voices.
#------------------------------------------------------------------------

from isobar_ext import *

import logging

def main():
    timeline = Timeline(100)

    timeline.schedule({
        "note": 60 * PEuclidean(5, 8),
        "duration": 0.25
    }, delay=0.0)
    timeline.schedule({
        "note": 62 * PEuclidean(5, 13),
        "duration": 0.5
    }, delay=0.25)
    timeline.schedule({
        "note": 64 * PEuclidean(7, 15),
        "duration": 0.5
    }, delay=0.5)
    timeline.schedule({
        "note": 67 * PEuclidean(6, 19),
        "duration": 0.25
    }, delay=0.75)
    timeline.schedule({
        "note": 71 * PEuclidean(7, 23),
        "duration": 0.5
    }, delay=1.0)

    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
