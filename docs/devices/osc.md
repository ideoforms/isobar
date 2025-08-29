# OpenSoundControl

isobar can be used to send [Open Sound Control](https://ccrma.stanford.edu/groups/osc/index.html) events to local or remote network hosts.

To send a sequence of events to an OSC device: 

```python
osc_device = iso.OSCOutputDevice("127.0.0.1", 8010)
timeline = iso.Timeline(120, output_device=osc_device)
timeline.schedule({
    "osc_address": "/freq",
    "osc_params": [
        iso.PSequence([440, 880])
    ]
})
```

In the above:
- `osc_address` is the OSC address path 
- `osc_params` is an optional list of zero or more arguments, which can be of type `int`, `float`, `bool`, or `str`. Each argument's OSC type is automatically inferred from its Python type.

Control-rate [interpolation](../events/control.md#interpolation) is not yet supported for OSC.