# MIDI file

## MidiFileOutputDevice

Writing MIDI files is done by setting the output device of a Timeline to a `MidiFileOutputDevice`

isobar normally generates events in real-time according to the tempo of the Timeline. To batch process events instantaneously, set the tempo of the timeline to `iso.MAX_CLOCK_RATE`. 

```
filename = "output.mid"
output = MidiFileOutputDevice(filename)

timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=output)
timeline.stop_when_done = True
timeline.schedule({ "note": iso.PSequence([ 60, 62, 64, 65 ], 1) })

timeline.run()
output.write()
```

## MidiFileInputDevice

Reading MIDI files is done with a `MidiFileInputDevice`.

The method `MidiFileInputDevice.read()` returns a `PDict` containing `PSequence`
patterns for each of the MIDI event properties (note, amplitude, duration), which
can be scheduled for playback within a timeline:

```python
pattern = MidiFileInputDevice(args.filename).read()
timeline = iso.Timeline()
timeline.schedule(pattern)
timeline.run()
```

To discard the amplitudes and durations, and make use of just the pitch values:

```python
pattern = MidiFileInputDevice(args.filename).read()
timeline = iso.Timeline()
timeline.schedule({
    "note": pattern["note"],
    "duration": 0.1
})
timeline.run()
```