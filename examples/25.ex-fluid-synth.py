#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-fluid-synth
# 
# Sequencing the free FluidSynth software soundfont synthesizer
# https://www.fluidsynth.org/
#------------------------------------------------------------------------

from isobar import *
from isobar.io.fluidsynth import FluidSynthOutputDevice
import logging
import argparse

def main(args):
    #------------------------------------------------------------------------
    # Initialise FluidSynth and select programs for three channels
    #------------------------------------------------------------------------
    output_device = FluidSynthOutputDevice(soundfont_path=args.soundfont_path,
                                           presets=[0, 5, 10])
    timeline = Timeline(120, output_device=output_device)
    
    #------------------------------------------------------------------------
    # Schedule a set of interlocking melodies.
    #------------------------------------------------------------------------
    for n in range(3):
        timeline.schedule({
            "key": Key("C", "minorPenta"),
            "octave": random.choice([4, 5, 6]),
            "degree": PLoop(PSubsequence(PWhite(0, 12),
                                0, 8)),
            "duration": PLoop(PSubsequence(PChoice([0.25, 0.5, 1.0], [1, 0.5, 0.25]),
                                    0, 6)),
            "channel": n
        }, quantize=None)
    
    timeline.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("soundfont_path", help="Path to an .sf2 file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main(args)
