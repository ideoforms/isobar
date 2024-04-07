#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-markov:
#
# Apply first-order Markov chains to an input MIDI file.
#------------------------------------------------------------------------

from isobar_ext import *
import argparse
# import isobar as iso
# from isobar.io.midifile.input import MidiFileInputDevice

import logging

def main():
    parser = argparse.ArgumentParser(description="Read and play a .mid file")
    parser.add_argument("filename", type=str, help="File to load (.mid)")
    args = parser.parse_args()

    #------------------------------------------------------------------------
    # Quantize durations to the nearest 1/8th note.
    #------------------------------------------------------------------------
    pattern = MidiFileInputDevice(args.filename).read(quantize=1 / 8)
    pattern = PDict(pattern)

    #------------------------------------------------------------------------
    # Learn note, duration and amplitude series separately.
    #------------------------------------------------------------------------
    note_learner = MarkovLearner()
    note_learner.learn_pattern(pattern["note"])
    dur_learner = MarkovLearner()
    dur_learner.learn_pattern(pattern["duration"])

    #------------------------------------------------------------------------
    # Quantize velocities to the nearest 10 to make chains easier to
    # learn with a small sample set.
    #------------------------------------------------------------------------
    amp_learner = MarkovLearner()
    amp_learner.learn_pattern(PInt(PRound(PScalar(pattern["amplitude"]), -1)))

    #------------------------------------------------------------------------
    # The markov property of a learner is a PMarkov, which generates
    # outputs by traversing the Markov chain stochastically.
    #------------------------------------------------------------------------
    timeline = Timeline(90)
    timeline.schedule({
        "note": note_learner.markov,
        "duration": dur_learner.markov,
        "amplitude": amp_learner.markov
    })

    try:
        timeline.run()
    except KeyboardInterrupt:
        timeline.output_device.all_notes_off()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()