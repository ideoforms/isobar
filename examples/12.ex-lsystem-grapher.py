#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-lsystem-grapher
#
# Generates an L-system and its ASCII representation.
#------------------------------------------------------------------------

import isobar as iso
import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

seq = iso.PLSystem("N[+N+N]?N[-N]+N", depth=3)
notes = seq.all()
note_min = min(notes)
note_max = max(notes)

for note in seq:
    note = note - note_min
    print("#" * note)
