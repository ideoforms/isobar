#!/usr/bin/env python3

import isobar as iso

import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

#------------------------------------------------------------------------
# walk up and down a minor scale
#------------------------------------------------------------------------
scale = iso.Scale([0, 2, 3, 7, 9, 11])
degree = iso.PBrown(0, 2, -8, 16, repeats=False)
notes = iso.PDegree(degree, scale) + 60

#------------------------------------------------------------------------
# add a slight 4/4 emphasis and moderate variation in velocity
#------------------------------------------------------------------------
amp = iso.PSequence([40, 30, 20, 25]) + iso.PBrown(0, 2, -10, 10)

timeline = iso.Timeline(170)
timeline.schedule({
    iso.EVENT_NOTE: notes,
    iso.EVENT_DURATION: 0.25,
    iso.EVENT_GATE: 0.9,
    iso.EVENT_AMPLITUDE: amp})
timeline.run()
