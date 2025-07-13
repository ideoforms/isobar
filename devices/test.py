from isobar import *
from signalflow import *

class Ping (Patch):
    def __init__(self, frequency: float = 440):
        super().__init__()
        sine = SineOscillator(frequency)
        envelope = ASREnvelope(0, 0, 0.5)
        output = sine * envelope * 0.25
        self.set_output(output)
        self.set_auto_free(True)

timeline = Timeline(120, SignalFlowOutputDevice())
timeline.schedule({
    # If a Patch class is passed to the `patch` property, a patch of this class
    # is created each time the event is triggered.
    "patch": Ping,
    "duration": 0.25,
    "params": {
        "frequency": PChoice([220, 440, 660, 880]),
    }
})
timeline.run()
