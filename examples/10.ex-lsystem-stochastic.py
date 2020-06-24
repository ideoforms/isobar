#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-lsystem-stochastic
#
# Generates a stochastic L-system arpeggio
#------------------------------------------------------------------------

import isobar as iso
from isobar.io.midi import MidiOut

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

notes = iso.PLSystem("N[+N--?N]+N[+?N]", depth=4)
notes = iso.PDegree(notes, iso.Scale.majorPenta)
notes = notes % 36 + 52

timeline = iso.Timeline(180)

timeline.schedule({
    "note": notes,
    "duration": 0.25
})
timeline.run()
