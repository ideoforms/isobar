#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-lsystem-rhythm
#
# Generates a rhythm line based on an L-system sprouting structure,
# sending output over MIDI.
#------------------------------------------------------------------------

import isobar as iso
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

#------------------------------------------------------------------------
# Generate a set of pitches based on an l-system, with recursive depth 4.
# symbols:
#  N = generate note node
#  + = transpose up one semitone
#  - = transpose down one semitone
#  [ = enter recursive branch
#  ] = leave recursive branch
#------------------------------------------------------------------------
notes = iso.PLSystem("N+[+N+N--N+N]+N[++N]", depth=4)
notes = notes + 60

#------------------------------------------------------------------------
# use another l-system to generate time intervals.
# take absolute values so that intervals are always positive.
#------------------------------------------------------------------------
times = iso.PLSystem("[N+[NN]-N+N]+N-N+N", depth=3)
times = iso.PAbs(iso.PDiff(times)) * 0.25

#------------------------------------------------------------------------
# ...and another l-system for amplitudes.
#------------------------------------------------------------------------
velocity = (iso.PLSystem("N+N[++N+N--N]-N[--N+N]") + iso.PWhite(-4, 4)) * 8
velocity = iso.PAbs(velocity)

timeline = iso.Timeline(120)
timeline.schedule({
    "note": notes,
    "amplitude": velocity,
    "duration": times
})
timeline.run()
