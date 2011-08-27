#!/usr/bin/python

# example-lsystem-grapher:
# generates an l-system and its ASCII representation

# import important things from isobar namespace.
from isobar import *
from isobar.io.midiout import *

import random
import time

seq = PLSys("N[+N+N]?N[-N]+N", depth = 3)
notes = seq.all()
low = min(notes)
hi = max(notes)
strings = [ "" for n in xrange(low, hi) ]
for note in notes:
	for n in xrange(low, hi):
		strings[n - low] += (" " if n >= note else "#")

strings.reverse()
for string in strings:
	print string


