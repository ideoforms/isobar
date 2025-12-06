from .. import *
from .abbreviations import *
from .setup import timeline, track, graph, live_set, open_set, lfo, tempo
from ..effects import *


try:
    import signalflow
    from .patches import segmenter
    from .sync import start_sync_test, stop_sync_test   
except ModuleNotFoundError:
    pass


from signalflow import Buffer

import glob
import os

def init_chord_scheme(chords):
    from signalflow_midi import MIDIManager

    try:
        manager = MIDIManager("Xkey25 USB")
        timeline.defaults.key = pglobals("key", chords[0]["key"])
        Globals.set("transpose", chords[0]["transpose"])
        for chord in chords:        
            note = 60 + chord["transpose"]
            manager.add_note_handler(note, lambda note, velocity, chord=chord: Globals.set(chord))
        print("Xkey25 control mappings set up.")
    except OSError:
        print("Xkey25 not found, skipping control mappings.")