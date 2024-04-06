# MIDI file

## MidiFileOutputDevice

Writing MIDI files is done by setting the output device of a Timeline to a `MidiFileOutputDevice`

isobar-ext normally generates events in real-time according to the tempo of the Timeline. To batch process events instantaneously, set the tempo of the timeline to `iso.MAX_CLOCK_RATE`. 

Multi track midi files are possible - see `sel_track` parameter.

```
filename = "output.mid"
output = MidiFileOutputDevice(filename)

timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=output)
timeline.stop_when_done = True

timeline.schedule({ "note": iso.PSequence([ 60, 62, 64, 65 ], 1)}, sel_track=0)
timeline.schedule({ "note": iso.PSequence([ 71, 72, 74, 75 ], 1)}, sel_track=1)

timeline.run()
output.write()
```
Mutlitrack with list of dictionary provided:
```
filename = "output.mid"
output = MidiFileOutputDevice(filename)

timeline = iso.Timeline(iso.MAX_CLOCK_RATE, output_device=output)
timeline.stop_when_done = True
events_1 = { "note": iso.PSequence([ 60, 62, 64, 65 ], 1), "args":  {'track_idx': 0}}
events_2 = { "note": iso.PSequence([ 71, 72, 74, 75 ], 1), "args":  {'track_idx': 1}}

timeline.schedule({ "note": iso.PSequence([ 60, 62, 64, 65 ], 1)}, sel_track=0)
timeline.schedule({ "note": iso.PSequence([ 71, 72, 74, 75 ], 1)}, sel_track=1)

timeline.run()
output.write()
```

events_1 = {
    iso.EVENT_NOTE: iso.PSequence(sequence=[50, 52, 55, 57], repeats=1)
    , iso.EVENT_DURATION: iso.PSequence(sequence=[0.5, 1, 1, 1.5], repeats=1)
    , iso.EVENT_CHANNEL: 0
    , iso.EVENT_ACTION_ARGS: {'track_idx': 0}
}

events_2 = {
    iso.EVENT_NOTE: iso.PSequence(sequence=[75, 69, 72, 66], repeats=1)
    , iso.EVENT_DURATION: iso.PSequence(sequence=[1, 1, 1, 1], repeats=1)
    , iso.EVENT_CHANNEL: 2
    , iso.EVENT_ACTION_ARGS: {'track_idx': 5}
}

## MidiFileInputDevice

Reading MIDI files is done with a `MidiFileInputDevice`.

The method `MidiFileInputDevice.read()` returns a `PDict` containing `PSequence`
patterns for each of the MIDI event properties (note, amplitude, duration, action), 
or with optional `MidiFileInputDevice.read(multi_track_file=True)` returns list of `PDict`:s containing `PSequence` which
can be scheduled for playback within a timeline:

#### Single track read
```python
pattern = MidiFileInputDevice(args.filename).read()
timeline = iso.Timeline()
timeline.schedule(pattern)  
timeline.run()
```
#### Multi track read
```python
pattern = MidiFileInputDevice(args.filename).read(multi_track_file=True)
timeline = iso.Timeline()
timeline.schedule(pattern)  
timeline.run()
```

Parameter `multi_track_file`  is optional with default value `False` to ensure backward compatibility between `isobar-ext` on single track `isobar`.  Additionally `isobar-ext` handles effectively action events (e.g. `set_tempo` midi message).


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