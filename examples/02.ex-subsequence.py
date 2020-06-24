#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-subsequence
#------------------------------------------------------------------------

import isobar as iso

import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

scale = iso.Scale.pelog
sequence = iso.PDegree(iso.PBrown(0, 3, -12, 12), scale)

offset = iso.PStutter(iso.pattern.PWhite(0, 4), 2)
sequence = iso.PSubsequence(sequence, offset, 4)
sequence = iso.PPermut(sequence)
sequence = sequence + 64
sequence = iso.PReset(sequence, iso.PImpulse(24))

amp = iso.pattern.PSequence([45, 35, 25, 40]) + iso.PBrown(0, 1, -15, 10)

gate = iso.pattern.PBrown(1.5, 0.01, 0.6, 2.5)

timeline = iso.Timeline(120)
timeline.schedule({
    "note": sequence.copy(),
    "amplitude": amp.copy(),
    "duration": 0.25,
    "gate": gate.copy()
})
timeline.schedule({
    "note": sequence.copy() + 24,
    "amplitude": amp.copy(),
    "duration": 0.5,
    "gate": gate.copy()
})
timeline.schedule({
    "note": sequence.copy() - 24,
    "amplitude": 10 + amp.copy() * 0.5,
    "duration": iso.PChoice([4, 4, 6, 8]),
    "gate": gate.copy()
})

timeline.run()
