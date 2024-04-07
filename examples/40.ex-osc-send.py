#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-osc-send
#
# Send OSC messages with a specified pattern.
#------------------------------------------------------------------------

from isobar_ext import *

def main():
    osc_device = OSCOutputDevice("127.0.0.1", 8010)
    timeline = Timeline(120, output_device=osc_device)
    timeline.schedule({
        "osc_address": "/freq",
        "osc_params": [PSequence([440, 880])]
    })
    timeline.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
