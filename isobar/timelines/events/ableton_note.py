from __future__ import annotations

from .midi_note import MidiNoteEvent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track

class AbletonMidiNoteEvent (MidiNoteEvent):
    def __init__(self, event_values: dict, track):
        super().__init__(event_values, track)
        # self.live_track = event_values["live_track"]