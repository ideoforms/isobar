from .util import midi_note_to_note_name

class Note(object):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, note=60, velocity=64, duration=1.0):
        self.note = note
        self.velocity = velocity
        self.duration = duration

    def __str__(self):
        if self.velocity == 0:
            return "rest"

        return midi_note_to_note_name(self.midinote)

    @staticmethod
    def all():
        return Note.names

Note.rest = Note(0, 0, 0)
