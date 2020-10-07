# Timelines

A `Timeline` schedules and executes events following a clock.

By default, a Timeline creates its own internal clock at a specified tempo:

```python
timeline = iso.Timeline(120)
timeline.run()
```

You can set and query the tempo using the `tempo` property:

```python
>>> timeline.tempo = 140
>>> print(timeline.tempo)
140
```

## Sync from clock in

A Timeline can be synchronised from an external MIDI clock:

```python
midi_in = MidiInputDevice()
timeline = iso.Timeline(clock_source=midi_in)
timeline.run()
```

MIDI `start` and `stop` events will be followed. Querying the timeline's `tempo` will give an estimate of the current bpm based on a moving average.

## Sync to clock out

You can also drive external MIDI clocks from a Timeline, by specifying the `send_clock` argument when creating the output device.

```python
output_device = iso.MidiOutputDevice(send_clock=True)
timeline = iso.Timeline(120, output_device=output_device)
timeline.run()
```

## Scheduling events

Scheduling events is done by passing a dict to the `Timeline.schedule()` method, which creates a new `Track` on the timeline. A timeline can have an unlimited number of tracks (unless you specify a limit with the `max_tracks` property).  

```python
#--------------------------------------------------------------------------------
# Play a series of 5 notes with random velocities.
# Delay by 1 beat before playback.
#--------------------------------------------------------------------------------
timeline = iso.Timeline(120)
timeline.schedule({
    "note": iso.PSequence([ 60, 67, 72, 77, 84 ], 1),
    "duration": 0.5,
    "amplitude": iso.PWhite(0, 128)
}, delay=1)
timeline.run()
```

Scheduling can be quantized or delayed by passing args to the `schedule()` method:

- `quantize=N`: quantize to the next `N` beats before beginning playback. For example, `quantize=1` will quantize to the next beat. `quantize=0.25` will quantize to a quarter-beat.
- `delay=N`: delay by `N` beats before beginning playback. If `quantize` and `delay` are both specified, quantization is applied, and the event is scheduled `delay` beats after the quantization time.

To limit the number of iterations of an event, pass the `count` property:

```
timeline.schedule({
    "note": iso.PSeries(0, 1) + 60
}, count=4)
```

## Clock resolution and accuracy

isobar's internal clock by default has a resolution of 480 ticks per beat (PPQN), which equates to a timing precision of 1ms at 120bpm.

High-precision scheduling in Python is inherently limited by Python's global interpreter lock (GIL), which means that sub-millisecond accuracy is unfortunately not possible. The good news is that, when using Python 3+, jitter is pretty low: the unit test suite verifies that the host device is able to keep time to +/- 1ms, and passes on Linux and macOS. 

## Nonlinear time

Time warping and nonlinear time is a work in progress.

