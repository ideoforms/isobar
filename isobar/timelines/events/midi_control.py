from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from .midi import MidiEvent
from ...constants import EVENT_TYPE_CONTROL, EVENT_CONTROL, EVENT_VALUE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track

class MidiControlChangeEvent(MidiEvent):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)
        self.type = EVENT_TYPE_CONTROL
        self.control = event_values[EVENT_CONTROL]
        self.value = event_values[EVENT_VALUE]

    def perform(self) -> None:
        self.output_device.control(self.control, self.value, self.channel)
        return True