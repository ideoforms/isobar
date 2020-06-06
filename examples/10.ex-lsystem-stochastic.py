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

midi = MidiOut()

timeline = iso.Timeline(120)
timeline.add_output(midi)

timeline.schedule({
    iso.EVENT_NOTE: notes,
    iso.EVENT_DURATION: 0.1
})
timeline.run()
