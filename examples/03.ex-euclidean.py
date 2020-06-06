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
    iso.EVENT_NOTE: 60 * iso.PEuclidean(5, 8),
    iso.EVENT_DURATION: 0.25
}, delay=0.0)
timeline.schedule({
    iso.EVENT_NOTE: 62 * iso.PEuclidean(5, 13),
    iso.EVENT_DURATION: 0.5
}, delay=0.25)
timeline.schedule({
    iso.EVENT_NOTE: 64 * iso.PEuclidean(7, 15),
    iso.EVENT_DURATION: 0.5
}, delay=0.5)
timeline.schedule({
    iso.EVENT_NOTE: 67 * iso.PEuclidean(6, 19),
    iso.EVENT_DURATION: 0.25
}, delay=0.75)
timeline.schedule({
    iso.EVENT_NOTE: 71 * iso.PEuclidean(7, 23),
    iso.EVENT_DURATION: 0.5
}, delay=1.0)

timeline.run()