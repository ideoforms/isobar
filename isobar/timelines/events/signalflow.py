from __future__ import annotations

from .event import Event
from ...constants import EVENT_PATCH, EVENT_TYPE, EVENT_PATCH_OUTPUT, EVENT_PATCH_PARAMS, EVENT_NOTE, EVENT_TRIGGER_NAME, EVENT_TRIGGER_VALUE
from ...constants import EVENT_TYPE_PATCH_CREATE, EVENT_TYPE_PATCH_TRIGGER, EVENT_TYPE_PATCH_SET

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..track import Track


class SignalFlowEvent(Event):
    def __init__(self, event_values: dict, track: Track):
        super().__init__(event_values, track)

        #----------------------------------------------------------------------
        # Patches support different event types:
        #  - create from PatchSpec or Patch class (EVENT_TYPE_PATCH_CREATE)
        #  - trigger Patch (EVENT_TYPE_PATCH_TRIGGER)
        #  - set Patch params (EVENT_TYPE_PATCH_SET)
        #----------------------------------------------------------------------
        self.patch = event_values[EVENT_PATCH]
        self.output = None

        if EVENT_TYPE in event_values:
            self.type = event_values[EVENT_TYPE]
        else:
            if type(self.patch).__name__ == "PatchSpec" or isinstance(self.patch, type):
                self.type = EVENT_TYPE_PATCH_CREATE
            else:
                if hasattr(self.patch, "trigger_node") and self.patch.trigger_node is not None:
                    self.type = EVENT_TYPE_PATCH_TRIGGER
                else:
                    self.type = EVENT_TYPE_PATCH_SET

        if EVENT_PATCH_OUTPUT in event_values:
            self.output = event_values[EVENT_PATCH_OUTPUT]

        self.params = {}
        if EVENT_PATCH_PARAMS in event_values:
            self.params = event_values[EVENT_PATCH_PARAMS]

        if EVENT_NOTE in event_values:
            self.note = event_values[EVENT_NOTE]

        self.trigger_name = None
        self.trigger_value = None
        if EVENT_TRIGGER_NAME in event_values:
            self.trigger_name = event_values[EVENT_TRIGGER_NAME]
        if EVENT_TRIGGER_VALUE in event_values:
            self.trigger_value = event_values[EVENT_TRIGGER_VALUE]