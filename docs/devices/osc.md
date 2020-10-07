# OpenSoundControl

To send a sequence of events to an OSC device: 

```python
osc_device = iso.OSCOutputDevice("127.0.0.1", 8010)
timeline = iso.Timeline(120, output_device=osc_device)
timeline.schedule({
    "osc_address": "/freq",
    "osc_params": [ iso.PSequence([ 440, 880 ]) ]
})
```

Control-rate [interpolation](../events/control.md#interpolation) is not yet supported for OSC.