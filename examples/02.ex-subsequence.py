#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-subsequence
#------------------------------------------------------------------------

import isobar as iso

import logging

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

scale = iso.Scale.pelog
sequence = iso.PDegree(iso.PBrown(0, 3, -12, 12, repeats=False), scale)

offset = iso.PStutter(iso.pattern.PWhite(0, 4), 2)
sequence = iso.PSubsequence(sequence, offset, 4)
sequence = iso.PPermut(sequence)
sequence = sequence + 64
sequence = iso.PReset(sequence, iso.PImpulse(24))

amp = iso.pattern.PSequence([45, 35, 25, 40]) + iso.PBrown(0, 1, -15, 10)

gate = iso.pattern.PBrown(1.5, 0.01, 0.6, 2.5)

timeline = iso.Timeline(120)
timeline.schedule({
    iso.EVENT_NOTE: sequence.copy(),
    iso.EVENT_AMPLITUDE: amp,
    iso.EVENT_DURATION: 0.25,
    iso.EVENT_GATE: gate
})
timeline.schedule({
    iso.EVENT_NOTE: sequence.copy() + 24,
    iso.EVENT_AMPLITUDE: amp.copy(),
    iso.EVENT_DURATION: 0.5,
    iso.EVENT_GATE: gate.copy()
})
timeline.schedule({
    iso.EVENT_NOTE: sequence.copy() - 24,
    iso.EVENT_AMPLITUDE: 10 + amp.copy() * 0.5,
    iso.EVENT_DURATION: iso.PChoice([4, 4, 6, 8]),
    iso.EVENT_GATE: gate.copy()
})

timeline.run()
