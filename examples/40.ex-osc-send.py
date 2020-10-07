#!/usr/bin/env python3

#------------------------------------------------------------------------
# ex-osc-send
#
# Send OSC messages with a specified pattern.
#------------------------------------------------------------------------

import isobar as iso

osc_device = iso.OSCOutputDevice("127.0.0.1", 8010)
timeline = iso.Timeline(120, output_device=osc_device)
timeline.schedule({
    "osc_address": "/freq",
    "osc_params": [iso.PSequence([440, 880])]
})
timeline.run()
