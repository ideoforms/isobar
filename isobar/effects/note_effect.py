from ..pattern import Pattern
from ..timelines.midi_note import MidiNoteInstance

class NoteEffect:
    def __init__(self):
        self.track = None
        self.effects = []

    def __gt__(self, other):
        if isinstance(other, NoteEffect):
            if self.track:
                return (self.track > other)
            else:
                self.effects.append(other)
                return self
        else:
            raise NotImplementedError("Cannot compare NoteEffect with %s" % type(other))

    def apply_chained_effects(self, note: MidiNoteInstance):
        for effect in self.effects:
            effect.apply(note)

class NoteEffectEcho (NoteEffect):
    def __init__(self, active=1, delay=0.5, count=1, scale=1.0, insert: NoteEffect = None):
        super().__init__()
        self.active = Pattern.pattern(active)
        self.delay = Pattern.pattern(delay)
        self.count = Pattern.pattern(count)
        self.scale = Pattern.pattern(scale)
        self.insert = Pattern.pattern(insert)

    def apply(self, note: MidiNoteInstance):
        active = Pattern.value(self.active)
        insert = Pattern.value(self.insert)
        if not active:
            return
        
        count = Pattern.value(self.count)
        for i in range(count):
            note_copy = note.copy()
            note_copy.timestamp += Pattern.value(self.delay * (i + 1))
            note_copy.amplitude = int(round(note_copy.amplitude * Pattern.value(self.scale)))
            if insert is not None:
                insert.apply(note_copy)
            note_copy.origin = self
            self.apply_chained_effects(note_copy)
            note.track.schedule_note(note_copy)

class NoteEffectTranspose(NoteEffect):
    def __init__(self, active=1, transpose=0):
        super().__init__()
        self.active = Pattern.pattern(active)
        self.transpose = Pattern.pattern(transpose)

    def apply(self, note: MidiNoteInstance):
        active = Pattern.value(self.active)
        if not active:
            return

        note.note += Pattern.value(self.transpose)

class NoteEffectScale(NoteEffect):
    def __init__(self, active=1, scale=0.5):
        super().__init__()
        self.active = Pattern.pattern(active)
        self.scale = Pattern.pattern(scale)

    def apply(self, note: MidiNoteInstance):
        active = Pattern.value(self.active)
        if not active:
            return

        note.amplitude = int(round(note.amplitude * Pattern.value(self.scale)))

