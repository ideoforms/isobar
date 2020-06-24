#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-hello-world
# 
# Introductory example. Plays a one-octave chromatic scale.
# Make sure you have a MIDI device connected.
#------------------------------------------------------------------------

import isobar as iso

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

series = iso.PRange(60, 73, 1)
timeline = iso.Timeline(120)

timeline.schedule({
    "note": series,
    "duration": 1
})

timeline.run()
