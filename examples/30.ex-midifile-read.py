#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-midifile-read:
#
# Example of reading from a MIDI file in real time.
#------------------------------------------------------------------------

from isobar_ext import *
from isobar_ext.io import MidiFileInputDevice

import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="Read and play a .mid file")
    parser.add_argument("filename", type=str, help="File to load (.mid)")
    args = parser.parse_args()

    #--------------------------------------------------------------------------------
    # Read a MIDI file into a pattern.
    # The resulting pattern is a PDict, with keys containing patterns for each
    # of the event properties (note, duration, amplitude)
    #--------------------------------------------------------------------------------
    pattern = MidiFileInputDevice(args.filename).read(multi_track_file=True)
    print("Read pattern containing %d note events" % len(pattern["note"]))

    timeline = Timeline()
    timeline.schedule(pattern)
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()