from .util import midi_pitch_to_note_name

class Note(object):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, midinote=60, velocity=64, length=1):
        self.midinote = midinote
        self.velocity = velocity
        self.length = length

    def __str__(self):
        if self.velocity == 0:
            return "rest"

        return midi_pitch_to_note_name(self.midinote)

    @staticmethod
    def all():
        return Note.names

Note.rest = Note(0, 0, 0)