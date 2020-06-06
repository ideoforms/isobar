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

series = iso.PRange(0, 73, 1)
timeline = iso.Timeline(120)

timeline.schedule({
    iso.EVENT_NOTE: series,
    iso.EVENT_DURATION: 1
})

timeline.run()
