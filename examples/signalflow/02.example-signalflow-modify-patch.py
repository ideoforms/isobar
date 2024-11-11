#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Example: Sequencing the SignalFlow DSP package.
# 
# Requires signalflow: pip3 install signalflow
#
# In this example, a Squelch patch is created at initialisation.
# Each event updates the inputs of the Squelch patch with new values.
#--------------------------------------------------------------------------------

from isobar import *
from signalflow import *

class Squelch (Patch):
    def __init__(self, cutoff: float = 110, resonance: float = 0.8):
        super().__init__()
        cutoff = self.add_input("cutoff", cutoff)
        resonance = self.add_input("resonance", resonance)
        square = SquareOscillator([55, 56])
        output = SVFilter(square, "low_pass", cutoff, resonance) * 0.25
        self.set_output(output)

graph = AudioGraph()
output_device = SignalFlowOutputDevice(graph=graph)

patch = Squelch()
patch.play()

timeline = Timeline(120, output_device=output_device)
timeline.schedule({
    "type": "set",
    "patch": patch,
    "duration": 0.25,
    "params": {
        "cutoff": PChoice([110, 220, 440, 880, 1760, 3520]),
        "resonance": PWhite(0.1, 0.99)
    }
})
timeline.run()

