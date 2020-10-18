# Getting started

## Requirements

isobar has been tested on Linux (Ubuntu, Raspberry Pi OS) and macOS. It has not been officially tested on Windows, although third-party contributions of support and QA efforts would be welcomed.

It requires Python 3.5 or above. 

On Linux, the `libasound` and `libjack-dev` packages are also required:

```
apt install libasound2-dev libjack-dev
```

### 1. Install isobar

The simplest way to install isobar is via `pip`:

```python
pip3 install isobar
```

To download the examples, you will need to clone the repo and install from source:

```python
git clone https://github.com/ideoforms/isobar.git
cd isobar
pip3 install .
```

### 2. Set up an output device

The example scripts are based on sending MIDI to a DAW or MIDI-compatible hardware instrument.
By default, isobar uses the system's default MIDI output as its output device.
If you want to specify a non-standard MIDI output, you can specify it using an environmental variable:

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

- [Code examples](https://github.com/ideoforms/isobar/tree/master/examples)
- Read about [Patterns](patterns/index.md), [Timelines](timelines/index.md), [Events](events/index.md) and [Devices](devices/index.md),
