#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-markov:
#
# Apply first-order Markov chains to an input MIDI file.
#------------------------------------------------------------------------

import argparse
import isobar as iso
from isobar.io.midifile.input import MidiFileInputDevice

import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")

parser = argparse.ArgumentParser(description="Read and play a .mid file")
parser.add_argument("filename", type=str, help="File to load (.mid)")
args = parser.parse_args()

#------------------------------------------------------------------------
# Quantize durations to the nearest 1/8th note.
#------------------------------------------------------------------------
pattern = MidiFileInputDevice(args.filename).read(quantize=1 / 8)
pattern = iso.PDict(pattern)

#------------------------------------------------------------------------
# Learn note, duration and amplitude series separately.
#------------------------------------------------------------------------
note_learner = iso.MarkovLearner()
note_learner.learn_pattern(pattern["note"])
dur_learner = iso.MarkovLearner()
dur_learner.learn_pattern(pattern["duration"])

#------------------------------------------------------------------------
# Quantize velocities to the nearest 10 to make chains easier to
# learn with a small sample set.
#------------------------------------------------------------------------
amp_learner = iso.MarkovLearner()
amp_learner.learn_pattern(iso.PInt(iso.PRound(iso.PScalar(pattern["amplitude"]), -1)))

#------------------------------------------------------------------------
# The markov property of a learner is a PMarkov, which generates
# outputs by traversing the Markov chain stochastically.
#------------------------------------------------------------------------
timeline = iso.Timeline(90)
timeline.schedule({
    "note": note_learner.markov,
    "duration": dur_learner.markov,
    "amplitude": amp_learner.markov
})

try:
    timeline.run()
except KeyboardInterrupt:
    timeline.output_device.all_notes_off()
