#!/usr/bin/env python

#------------------------------------------------------------------------
# isobar: ex-lsystem-grapher
#
# Generates an L-system and its ASCII representation.
#------------------------------------------------------------------------

from isobar import *

import random
import time

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

seq = PLSys("N[+N+N]?N[-N]+N", depth=3)
notes = seq.all()
note_min = min(notes)
note_max = max(notes)

for note in seq:
    note = note - note_min
    print("#" * note)
