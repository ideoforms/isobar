# Control events

MIDI control change events can be sequenced by specifying the integer `control` index and the `value` to set the control change to:

```python
timeline.schedule({
    "control": 0,
    "value": iso.PWhite(0, 128),
    "duration": 0.5
})
```

The above example sets control index `0` to a value drawn from a uniformly distribution, once every half-beat. 

## Interpolation

To transmit smooth control curves, isobar can interpolate between control values. The resulting interpolated value is sent continuously to the output device.

```python
# Apply linear interpolation to smoothly fade between values.
timeline.schedule({
    "control": 0,
    "value": iso.PWhite(0, 128),
    "duration": 0.5
}, interpolate="linear")
``` 

To jump instantaneously between values when interpolation is being used, simply set a `duration` of zero. The below applies sawtooth-shaped modulation to a control signal.

```python
timeline.schedule({
    "control": 0,
    "value": iso.PSequence([ 0, 127 ]),
    "duration": iso.PSequence([ 1, 0 ])
}, interpolate="linear")
``` 

Interpolation modes include:

- `linear`
- `cosine` 