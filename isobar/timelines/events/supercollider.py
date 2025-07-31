from __future__ import annotations

from .event import Event
from ...constants import EVENT_TYPE_SUPERCOLLIDER, EVENT_SUPERCOLLIDER_SYNTH, EVENT_SUPERCOLLIDER_SYNTH_PARAMS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


class SuperColliderEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        self.type = EVENT_TYPE_SUPERCOLLIDER
        self.synth_name = event_values[EVENT_SUPERCOLLIDER_SYNTH]
        self.synth_params = {}
        if EVENT_SUPERCOLLIDER_SYNTH_PARAMS in event_values:
            if not isinstance(event_values[EVENT_SUPERCOLLIDER_SYNTH_PARAMS], dict):
                raise ValueError("SuperCollider params must be a dict")
            self.synth_params = event_values[EVENT_SUPERCOLLIDER_SYNTH_PARAMS]

    def perform(self) -> bool:
        self.track.output_device.create(self.synth_name, self.synth_params)
        return True