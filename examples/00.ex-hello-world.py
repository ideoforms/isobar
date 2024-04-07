#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-hello-world
# 
# Introductory example. Plays a one-octave chromatic scale.
# Make sure you have a MIDI device connected.
#------------------------------------------------------------------------

from isobar_ext import *

import logging

def main():
    series = PRange(60, 73, 1)
    timeline = Timeline(120)

    timeline.schedule({
        "note": series,
        "duration": 1
    })

    timeline.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
