# Getting started

## Requirements

isobar-ext has been tested on Linux (Ubuntu, Raspberry Pi OS) and macOS. It has not been officially tested on Windows, although third-party contributions of support and QA efforts would be welcomed. (to be verified)

It requires Python 3.5 or above. (to be verified rather 3.9+)

On Linux, the `libasound` and `libjack-dev` packages are also required:

```
apt install libasound2-dev libjack-dev
```

### 1. Install isobar-ext

The simplest way to install isobar is via `pip`:

```python
pip3 install isobar-ext
```

To download the examples, you will need to clone the repo and install from source:

```python
git clone https://github.com/pioteresk/isobar-ext.git
cd isobar-ext
pip3 install .
```

### 2. Set up an output device

The example scripts are based on sending MIDI to a DAW or MIDI-compatible hardware instrument.
By default, isobar-ext uses the system's default MIDI output as its output device.
If you want to specify a non-standard MIDI output, you can [specify the name of the MIDI device when creating the Timeline](devices/midi.md), or set a global default output device by using an environmental variable:

```python
export ISOBAR_DEFAULT_MIDI_OUT="Prophet 6"
```

When you run an example script, you can confirm that it is using the right output as it will print the name of the output device it is using.

### 3. Run an example

Inside the repo directory you cloned above, there are a number of example scripts.
To run the "hello world" example:

```python
python3 examples/00.ex-hello-world.py
``` 

The script will print the default MIDI driver to screen, and begin triggering notes.

!!! tip "Troubleshooting"
    If you don't hear any notes, check that:
    
    - the name of the correct device is printed to the console
    - your device is configured to listen for MIDI on channel 1, and can play the note 60
    
    Use a MIDI monitor utility to check that the events are registering correctly.

## Next steps

- [Code examples](https://github.com/piotereks/isobar-ext/tree/master/examples)
- Read about [Patterns](patterns/index.md), [Timelines](timelines/index.md), [Events](events/index.md) and [Devices](devices/index.md),
