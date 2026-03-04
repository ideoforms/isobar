from ..midinote import MidiNote

class DummyInputDevice:
    def __init__(self):
        self.on_note_on = None
        self.on_note_off = None
        
    def add_note_on_handler(self, callback):
        self.on_note_on = callback
        
    def add_note_off_handler(self, callback):
        self.on_note_off = callback
        
    def note_on(self, pitch, velocity, channel=0):
        if self.on_note_on:
            self.on_note_on(MidiNote(pitch=pitch, velocity=velocity, channel=channel))

    def note_off(self, pitch, channel=0):
        if self.on_note_off:
            self.on_note_off(MidiNote(pitch=pitch, velocity=0, channel=channel))