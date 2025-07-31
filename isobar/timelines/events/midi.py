from __future__ import annotations

from isobar.io.midi.output import MidiOutputDevice

from .event import Event
from ...constants import EVENT_CHANNEL

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track

class MidiEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)
        self.channel = event_values[EVENT_CHANNEL]

    @property
    def output_device(self) -> MidiOutputDevice:
        return self.track.output_device