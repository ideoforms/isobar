from __future__ import annotations

from .event import Event
from ...pattern import Pattern
from ...constants import EVENT_TYPE_ACTION, EVENT_ACTION, EVENT_ACTION_ARGS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


class ActionEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        self.type = EVENT_TYPE_ACTION
        self.action = event_values[EVENT_ACTION]
        self.args = {}
        if EVENT_ACTION_ARGS in event_values:
            self.args = dict((key, Pattern.value(value)) for key, value in event_values[EVENT_ACTION_ARGS].items())
