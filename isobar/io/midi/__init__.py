from .input import MidiInputDevice
from .output import MidiOutputDevice

import mido

def get_midi_output_names():
    """
    Query MIDI output device names.

    Returns:
        List[str]: A list of all possible MIDI output device names.
    """
    output_names = mido.get_output_names()
    return output_names

def get_midi_input_names():
    """
    Query MIDI input device names.

    Returns:
        List[str]: A list of all possible MIDI input device names.
    """
    input_names = mido.get_input_names()
    return input_names

__all__ = ["MidiInputDevice", "MidiOutputDevice", "get_midi_input_names", "get_midi_output_names"]

# Class aliases for backwards-compatibility
MidiOut = MidiOutputDevice
MidiIn = MidiInputDevice
