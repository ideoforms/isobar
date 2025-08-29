from __future__ import annotations

from .event import Event
from ...pattern import Pattern
from ...globals import Globals
from ...constants import EVENT_TYPE_GLOBAL, EVENT_GLOBAL, EVENT_VALUE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


class GlobalsEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        self.type = EVENT_TYPE_GLOBAL
        self.global_key = event_values[EVENT_GLOBAL]
        self.global_value = event_values.get(EVENT_VALUE, None)

    def perform(self) -> bool:
        #------------------------------------------------------------------------
        # Action: Set a global variable
        #------------------------------------------------------------------------
        key = Pattern.value(self.global_key)
        value = Pattern.value(self.global_value)
        Globals.set(key, value)
        return True