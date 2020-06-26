__version__ = "0"
__author__ = "Daniel Jones <http://www.erase.net/>"

from .dummy import DummyOutputDevice
from .midi import MidiIn, MidiOut, get_midi_output_names, get_midi_input_names
from .midifile import MidiFileIn, MidiFileOut, PatternWriterMIDI
from .osc import OSCOut
from .socketio import SocketIOOut
from .signalflow import SignalflowOutputDevice
from .midinote import MidiNote
from .supercollider import SuperColliderOutputDevice