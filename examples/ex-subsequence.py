#!/usr/bin/env python

from isobar import *

scale = Scale([ 0, 2, 3, 6, 7 ])
scale = Scale.pelog
seq = PDegree(PBrown(0, 3, -12, 12, repeats = False), scale)

offset = PStutter(PWhite(0, 4), 2)
seq = PSubsequence(seq, offset, 4)
seq = PPermut(seq)
seq = seq + 64
seq = PReset(seq, PImpulse(24))

amp = PSeq([ 45, 35, 25, 40 ]) + PBrown(0, 1, -15, 10)
amp = PSeq([ 45, 35, 35, 40 ]) + PBrown(0, 1, -15, 10)

gate = PBrown(1.5, 0.01, 0.6, 2.5)

timeline = Timeline(120)
timeline.sched({ 'note': seq, 'amp': amp, 'dur': 0.25, 'gate': gate })
timeline.sched({ 'note': seq.copy() + 24, 'amp': amp.copy(), 'dur': 0.5, 'gate': gate.copy() })
timeline.sched({ 'note': seq.copy() - 24, 'amp': 10 + amp.copy() * 0.5, 'dur': PChoice([ 4, 4, 6, 8 ]), 'gate': gate.copy() })
timeline.run()

