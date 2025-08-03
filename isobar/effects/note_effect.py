from ..pattern import Pattern
from ..timelines.midi_note import MidiNoteInstance

class NoteEffect:
    def __init__(self):
        self.track = None

    def __gt__(self, other):
        if isinstance(other, NoteEffect):
            return (self.track > other)
        else:
            raise NotImplementedError("Cannot compare NoteEffect with %s" % type(other))


class NoteEffectEcho (NoteEffect):
    def __init__(self, active=1, delay=0.5, scale=1.0):
        super().__init__()
        self.active = active
        self.delay = delay
        self.scale = scale
    
    def apply(self, note: MidiNoteInstance):
        active = Pattern.value(self.active)
        if not active:
            return
        
        note_copy = note.copy()
        note_copy.timestamp += Pattern.value(self.delay)
        note_copy.amplitude = int(round(note_copy.amplitude * Pattern.value(self.scale)))
        note.track.schedule_note(note_copy, bypass_effects=True)

class NoteEffectScale(NoteEffect):
    def __init__(self, active=1, scale=0.5):
        super().__init__()
        self.active = active
        self.scale = scale

    def apply(self, note: MidiNoteInstance):
        active = Pattern.value(self.active)
        if not active:
            return

        note.amplitude = int(round(note.amplitude * Pattern.value(self.scale)))
