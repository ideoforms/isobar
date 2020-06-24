#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-euclidean
#
# Uses Euclidean rhythms to generate multiple polyrhythmic voices.
#------------------------------------------------------------------------

import isobar as iso

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

timeline = iso.Timeline(100)

timeline.schedule({
    "note": 60 * iso.PEuclidean(5, 8),
    "duration": 0.25
}, delay=0.0)
timeline.schedule({
    "note": 62 * iso.PEuclidean(5, 13),
    "duration": 0.5
}, delay=0.25)
timeline.schedule({
    "note": 64 * iso.PEuclidean(7, 15),
    "duration": 0.5
}, delay=0.5)
timeline.schedule({
    "note": 67 * iso.PEuclidean(6, 19),
    "duration": 0.25
}, delay=0.75)
timeline.schedule({
    "note": 71 * iso.PEuclidean(7, 23),
    "duration": 0.5
}, delay=1.0)

timeline.run()