# Timelines: Synchronisation with external clocks

isobar can synchronise with external clocks in a few different ways.

- MIDI: [Sync from MIDI clock in](#sync-from-midi-clock-in)
- MIDI: [Sync to MIDI clock out](#sync-to-midi-clock-out)
- [Ableton Link Clock](#ableton-link-clock)

## Sync from MIDI clock in

A Timeline can be synchronised from an external MIDI clock:

```python
midi_in = MidiInputDevice()
timeline = Timeline(clock_source=midi_in)
timeline.run()
```

MIDI transport events will be obeyed:

- `start` starts the timeline playback from time = 0
- `stop` stops the timeline
- `continue` resumes playback from wherever it was stopped

When synchronised to an external MIDI clock, querying the timeline's `tempo` will give an estimate of the current bpm based on a moving average.

## Sync to MIDI clock out

You can also drive external MIDI clocks from a Timeline, by specifying the `send_clock` argument when creating the output device.

```python
output_device = MidiOutputDevice(send_clock=True)
timeline = Timeline(120, output_device=output_device)
try:
    timeline.run()
except KeyboardInterrupt:
    # When ctrl-c is pressed, stop the timeline, which sends a MIDI `stop`
    # transport message to the external device.
    timeline.stop()
```

## Ableton Link clock

Playback can be synchronised with Ableton Live or other devices that support [Ableton Link](https://www.ableton.com/en/link/) clocking. Other Link processes on the same computer, or on the local network, are automatically detected.

Ensure that Ableton Live is running on the network with `Link` enabled. Run the below example, and you should hear that it is synchronised with Live's playback.

```
timeline = Timeline(clock_source="link")
timeline.schedule({
    "note": 60
}, quantize=1)
timeline.run()
```