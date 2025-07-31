from __future__ import annotations

from .event import Event
from ...constants import EVENT_TYPE_OSC, EVENT_OSC_ADDRESS, EVENT_OSC_PARAMS

from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from ..track import Track


class OscEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        self.type = EVENT_TYPE_OSC
        self.osc_address = event_values[EVENT_OSC_ADDRESS]
        self.osc_params = {}
        if EVENT_OSC_PARAMS in event_values:
            if not isinstance(event_values[EVENT_OSC_PARAMS], Iterable):
                raise ValueError("OSC params must be an iterable")
            self.osc_params = list(event_values[EVENT_OSC_PARAMS])

    
    def perform(self) -> bool:
        self.track.output_device.send(self.osc_address, self.osc_params)
        return True