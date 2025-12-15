import copy

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .track import Track

class MidiNoteInstance:
    def __init__(self,
                 timestamp: float,
                 track = None,
                 note: int = None,
                 amplitude: int = None,
                 duration: float = None,
                 channel: int = None,
                 pitchbend: int = 0,
                 params: dict = None):
        
        from ..effects.note_effect import NoteEffect

        self.track = track

        self._note = note
        self._amplitude = amplitude
        self._channel = channel
        self._timestamp = timestamp
        self._duration = duration
        self._pitchbend = pitchbend
        self._params = params
        self._ticks_remaining = None

        self.is_playing = False
        self.is_finished = False
        self.origin: NoteEffect = None

        # If True, the note is ephemeral (e.g. created by a realtime process),
        # and should not be stored in history.
        self.is_ephemeral = True

    def start_playing(self, duration_ticks: int) -> None:
        """
        Mark the note as playing and set the remaining ticks.

        Args:
            duration_ticks (int): The duration of the note in ticks.
        """
        self.is_playing = True
        self._ticks_remaining = duration_ticks - 1

    def tick(self) -> None:
        """
        Advance the note by one tick.
        """
        if self._ticks_remaining is None:
            return
        
        if self._ticks_remaining > 0:
            self._ticks_remaining -= 1
        else:
            if self._ticks_remaining == 0:
                self.is_finished = True

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
    
    def get_note(self) -> int:
        return self._note if self._note is not None else self.track.defaults.note
    def set_note(self, value: int):
        self._note = value
    def has_note(self) -> bool:
        return self._note is not None
    note = property(get_note, set_note)

    def get_amplitude(self) -> int:
        return self._amplitude if self._amplitude is not None else self.track.defaults.amplitude
    def set_amplitude(self, value: int):
        self._amplitude = value
    def has_amplitude(self) -> bool:
        return self._amplitude is not None
    amplitude = property(get_amplitude, set_amplitude)

    def get_channel(self) -> int:
        return self._channel if self._channel is not None else self.track.defaults.channel
    def set_channel(self, value: int):
        self._channel = value
    def has_channel(self) -> bool:
        return self._channel is not None
    channel = property(get_channel, set_channel)

    def get_timestamp(self) -> float:
        return self._timestamp
    def set_timestamp(self, value: float):
        self._timestamp = value
    def has_timestamp(self) -> bool:
        return self._timestamp is not None
    timestamp = property(get_timestamp, set_timestamp)
    
    def get_duration(self) -> float:
        return self._duration if self._duration is not None else self.track.defaults.duration
    def set_duration(self, value: float):
        self._duration = value
    def has_duration(self) -> bool:
        return self._duration is not None
    duration = property(get_duration, set_duration)
    
    def get_pitchbend(self) -> int:
        return self._pitchbend if self._pitchbend is not None else self.track.defaults.pitchbend
    def set_pitchbend(self, value: int):
        self._pitchbend = value
    def has_pitchbend(self) -> bool:
        return self._pitchbend is not None
    pitchbend = property(get_pitchbend, set_pitchbend)
    
    def get_params(self) -> dict:
        return self._params
    def set_params(self, value: dict):
        self._params = value
    def has_params(self) -> bool:
        return self._params is not None
    params = property(get_params, set_params)