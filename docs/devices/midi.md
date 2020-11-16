# MIDI

isobar's MIDI support is based on the excellent [mido](https://mido.readthedocs.io/en/latest/) library. 

Two classes are available for MIDI I/O:

## MidiOutputDevice

Sends note and control events to a MIDI device. isobar can also act as the clock out, so that external MIDI devices follow isobar's internal clock.  

!!! info "Virtual MIDI devices" 
    To control a MIDI device on the same computer that is running isobar, you will need to create a [virtual MIDI bus](https://help.ableton.com/hc/en-us/articles/209774225-How-to-setup-a-virtual-MIDI-bus).

```python
name = "My MIDI Device Name"
midi_out = iso.MidiOutputDevice(device_name=name,
                                send_clock=True)
timeline = Timeline(tempo=120, output_device=midi_out)
```

- `device_name`: Specifies the device name to search for. Leave empty to use the system default.
- `send_clock`: If True, sends clock sync signals to the external device.

A default MIDI output device name can be set with an environmental variable:

```
export ISOBAR_DEFAULT_MIDI_OUT="Prophet 6"
``` 

To list all available MIDI output devices:

```
print(iso.io.midi.get_midi_output_names())
```

## MidiInputDevice

Receives notes and control events from a MIDI device, or sync isobar to an external MIDI clock.

```python
# Receive MIDI messages from an external device 
name = "My MIDI Device Name"
midi_in = iso.MidiInputDevice(device_name=name)

# Blocking mode: waits until a message is received
message = midi_in.receive()

# Non-blocking: if a message is available, return it; otherwise, return None
message = midi_in.poll()
```

```python
# Sync a Timeline to a MIDI external clock 
name = "My MIDI Device Name"
midi_in = iso.MidiInputDevice(device_name=name)
timeline = Timeline(tempo=120, clock_source=midi_in)
```

A default MIDI input device name can be set with an environmental variable:

```
export ISOBAR_DEFAULT_MIDI_IN="Prophet 6"
``` 

To list all available MIDI input devices:

```
print(iso.io.midi.get_midi_input_names())
```

