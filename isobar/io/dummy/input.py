from ..midinote import MidiNote

class DummyInputDevice:
    def __init__(self):
        self.name = "Dummy Input Device"
        self.on_note_on_handlers: list[callable] = []
        self.on_note_off_handlers: list[callable] = []
        
    def add_note_on_handler(self, callback):
        self.on_note_on_handlers.append(callback)
        
    def add_note_off_handler(self, callback):
        self.on_note_off_handlers.append(callback)

    def remove_note_on_handler(self, callback):
        self.on_note_on_handlers.remove(callback)

    def remove_note_off_handler(self, callback):
        self.on_note_off_handlers.remove(callback)
        
    def note_on(self, pitch, velocity, channel=0):
        for handler in self.on_note_on_handlers:
            handler(MidiNote(pitch=pitch, velocity=velocity, channel=channel))

    def note_off(self, pitch, channel=0):
        for handler in self.on_note_off_handlers:
            handler(MidiNote(pitch=pitch, velocity=0, channel=channel))