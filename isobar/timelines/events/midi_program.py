from __future__ import annotations

from isobar.timelines.events import event

from .midi import MidiEvent
from ...constants import EVENT_TYPE_PROGRAM_CHANGE, EVENT_PROGRAM_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track

class MidiProgramChangeEvent(MidiEvent):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)
        self.type = EVENT_TYPE_PROGRAM_CHANGE
        self.program_change = event_values[EVENT_PROGRAM_CHANGE]

    def perform(self) -> bool:
        self.output_device.program_change(self.program_change,
                                          self.channel)
        return True
