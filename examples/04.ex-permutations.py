#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-permutations
# 
# PPermut generates every possible permutation of a sequence:
# [1, 2, 3] -> [1, 2, 3, 1, 3, 2, 2, 1, 3, 2, 3, 1, 3, 1, 2, 3, 2, 1]
#
# Use simple permutations to generate intertwining musical structures.
#------------------------------------------------------------------------

import isobar as iso
import random

#------------------------------------------------------------------------
# Create a pitch line comprised of multiple permutations on a pelog scale
#------------------------------------------------------------------------
ppitch = iso.PShuffle([random.randint(-6, 6) for n in range(6)])
ppitch = iso.PPermut(ppitch)
ppitch = iso.PDegree(ppitch, iso.Key("F#", "pelog"))

#------------------------------------------------------------------------
# Create permuted sets of durations and amplitudes.
# Different lengths mean poly-combinations.
#------------------------------------------------------------------------
pdur = iso.PShuffle([1, 1, 2, 2, 4], 1)
pdur = iso.PPermut(pdur) / 4

pamp = iso.PShuffle([10, 15, 20, 35], 2)
pamp = iso.PPermut(pamp)

#------------------------------------------------------------------------
# Schedule on a 60bpm timeline and send to MIDI output
#------------------------------------------------------------------------
timeline = iso.Timeline(60)
timeline.schedule({
    iso.EVENT_NOTE: ppitch + 60,
    iso.EVENT_DURATION: pdur,
    iso.EVENT_AMPLITUDE: pamp,
    iso.EVENT_CHANNEL: 0
})
timeline.schedule({
    iso.EVENT_NOTE: ppitch + 24,
    iso.EVENT_DURATION: pdur * 4,
    iso.EVENT_AMPLITUDE: pamp,
    iso.EVENT_CHANNEL: 1,
    iso.EVENT_GATE: 2
})
timeline.schedule({
    iso.EVENT_NOTE: ppitch + 72,
    iso.EVENT_DURATION: pdur / 2,
    iso.EVENT_CHANNEL: 1,
    iso.EVENT_GATE: 1,
    iso.EVENT_AMPLITUDE: pamp / 2
})

#------------------------------------------------------------------------
# Apply continuous time-warping to the timeline
#------------------------------------------------------------------------
warp = iso.PWInterpolate(iso.PBrown(-0.1, 0.01, -0.15, -0.05), 2)
timeline.warp(warp)

#------------------------------------------------------------------------
# Begin playback
#------------------------------------------------------------------------
timeline.run()
