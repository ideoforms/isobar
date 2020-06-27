#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-read:
#
# Example of reading from a MIDI file in real time.
#------------------------------------------------------------------------

import isobar as iso
from isobar.io import MidiFileInputDevice

import argparse
import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

parser = argparse.ArgumentParser(description="Read and play a .mid file")
parser.add_argument("filename", type=str, help="File to load (.mid)")
args = parser.parse_args()

pattern = iso.PDict()
pattern.load(args.filename)
print(pattern["note"])

timeline = iso.Timeline()
timeline.schedule(pattern)
timeline.run()
