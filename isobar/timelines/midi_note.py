import copy


class MidiNoteInstance:
    def __init__(self,
                 note: int,
                 amplitude: int,
                 channel: int,
                 timestamp: float,
                 duration: float,
                 pitchbend: int = 0):
        
        from .track import Track
        from ..effects.note_effect import NoteEffect

        self.note = note
        self.amplitude = amplitude
        self.channel = channel
        self.timestamp = timestamp
        self.duration = duration
        self.pitchbend = pitchbend

        self.is_playing = False
        self.track: Track = None
        self.origin: NoteEffect = None

    @property
    def note_off_time(self) -> float:
        """
        Calculate the time when the note should be released.
        """
        return self.timestamp + self.duration

    def __repr__(self):
        return f"MidiNoteInstance(note={self.note}, amplitude={self.amplitude}, channel={self.channel}, timestamp={self.timestamp}, duration={self.duration}, pitchbend={self.pitchbend})"
    
    def copy(self):
        return copy.copy(self)