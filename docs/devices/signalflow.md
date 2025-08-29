# SignalFlow

isobar can be used to control the [SignalFlow](https://signalflow.dev/) Python synthesis framework.

Three different types of event are supported, all of which interact with [Patch](https://signalflow.dev/patch/) objects:

- create a `Patch`
- modify a parameter of a `Patch`
- send a [trigger](https://signalflow.dev/patch/inputs/#triggers) event to a `Patch`

## Create a Patch

```python
from isobar import *
from signalflow import *

class Ping (Patch):
    def __init__(self, frequency: float = 440):
        super().__init__()
        sine = SineOscillator(frequency)
        envelope = ASREnvelope(0, 0, 0.5)
        output = sine * envelope * 0.25
        self.set_output(output)
        self.set_auto_free_node(envelope)

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
```

## Modify a parameter of a Patch

```python
from isobar import *
from isobar.io.signalflow import SignalFlowOutputDevice
from signalflow import *

class Tone (Patch):
    def __init__(self, frequency: float = 440):
        super().__init__()
        frequency = self.add_input("frequency", frequency)
        sine = SineOscillator(frequency)
        output = sine * 0.25
        self.set_output(output)

graph = AudioGraph()
output_device = SignalFlowOutputDevice(graph=graph)

patch = Tone()
patch.play()

timeline = Timeline(120, output_device=output_device)
timeline.schedule({
    "patch": patch,
    "duration": 0.25,
    "params": {
        "frequency": PChoice([220, 440, 660, 880]),
    }
})
timeline.run()
```

## Send a trigger event to a Patch

```python
from isobar import *
from isobar.io.signalflow import SignalFlowOutputDevice
from signalflow import *

class Cymbal (Patch):
    def __init__(self):
        super().__init__()
        noise = WhiteNoise()
        envelope = ASREnvelope(0, 0, 0.1)
        output = noise * envelope * 0.25
        self.set_output(output)
        self.set_trigger_node(envelope)

graph = AudioGraph()
output_device = SignalFlowOutputDevice(graph=graph)

cymbal = Cymbal()
cymbal.play()

timeline = Timeline(120, output_device=output_device)
timeline.schedule({
    "patch": cymbal,
    "type": "trigger",
    "duration": PLoop(PTri(10, 0.1, 0.5)),
})
timeline.run()
```
