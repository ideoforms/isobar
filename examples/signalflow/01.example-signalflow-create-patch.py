#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Example: Sequencing the SignalFlow DSP package.
# 
# Requires signalflow: pip3 install signalflow
#
# In this example, the timeline creates a new Ping patch for each event.
# Setting the auto_free property frees the patch after it finishes.
#--------------------------------------------------------------------------------

from isobar import *
from isobar.io import SignalFlowOutputDevice
from signalflow import *

class Ping (Patch):
    def __init__(self, frequency: float = 440):
        super().__init__()
        envelope = ASREnvelope(0, 0, 0.5)
        sine = SineOscillator(frequency)
        output = sine * envelope * 0.25
        output = StereoPanner(output)
        self.set_output(output)
        self.set_auto_free_node(envelope)

output_device = SignalFlowOutputDevice()
timeline = Timeline(120, output_device=output_device)
timeline.schedule({
    "type": "patch",
    "patch": Ping,
    "duration": 0.25,
    "params": {
        "frequency": PChoice([220, 440, 660, 880]),
    }
})
timeline.run()

