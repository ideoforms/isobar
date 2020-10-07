__version__ = "0"
__author__ = "Daniel Jones <http://www.erase.net/>"

from .output import OutputDevice
from .dummy import DummyOutputDevice
from .midi import MidiInputDevice, MidiOutputDevice, get_midi_output_names, get_midi_input_names
from .midifile import MidiFileInputDevice, MidiFileOutputDevice, PatternWriterMIDI
from .osc import OSCOutputDevice
from .socketio import SocketIOOutputDevice
from .signalflow import SignalflowOutputDevice
from .midinote import MidiNote
from .supercollider import SuperColliderOutputDevice

__all__ = ["OutputDevice", "DummyOutputDevice", "MidiInputDevice", "MidiOutputDevice"]
__all__ += ["get_midi_output_names", "get_midi_input_names"]
__all__ += ["MidiFileInputDevice", "MidiFileOutputDevice", "PatternWriterMIDI"]
__all__ += ["OSCOutputDevice", "SocketIOOutputDevice", "SignalflowOutputDevice",
            "MidiNote", "SuperColliderOutputDevice"]
