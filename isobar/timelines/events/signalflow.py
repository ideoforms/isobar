from __future__ import annotations

from .event import Event
from ...constants import EVENT_PATCH, EVENT_TYPE, EVENT_PATCH_OUTPUT, EVENT_PATCH_PARAMS, EVENT_NOTE, EVENT_TRIGGER_NAME, EVENT_TRIGGER_VALUE
from ...constants import EVENT_TYPE_PATCH_CREATE, EVENT_TYPE_PATCH_TRIGGER, EVENT_TYPE_PATCH_SET
from ...exceptions import InvalidEventException
from ...pattern import Pattern
from ...util import midi_note_to_frequency

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
    
    def perform(self) -> bool:
        #------------------------------------------------------------------------
        # SignalFlow patch
        #------------------------------------------------------------------------
        if self.type == EVENT_TYPE_PATCH_CREATE:
            #------------------------------------------------------------------------
            # Action: Create patch
            #------------------------------------------------------------------------
            if not hasattr(self.output_device, "create"):
                raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
            params = dict((key, Pattern.value(value)) for key, value in self.params.items())
            if hasattr(self, "note"):
                notes = self.note if hasattr(self.note, '__iter__') else [self.note]

                for note in notes:
                    if note > 0:
                        # TODO: Should use None to denote rests
                        params["frequency"] = midi_note_to_frequency(note)
                        self.output_device.create(self.patch, params, output=self.output)
            else:
                self.output_device.create(self.patch, params, output=self.output)

        elif self.type == EVENT_TYPE_PATCH_SET or self.type == EVENT_TYPE_PATCH_TRIGGER:
            #------------------------------------------------------------------------
            # Action: Set patch's input(s) and/or trigger an event
            # If any of the params return None, the event is treated as a rest,
            # and the patch is not triggered.
            #------------------------------------------------------------------------
            event_is_rest = False
            for key, value in self.params.items():
                value = Pattern.value(value)
                if value is None:
                    event_is_rest = True
                else:
                    self.patch.set_input(key, value)

            if hasattr(self, "note"):
                self.patch.set_input("frequency", midi_note_to_frequency(self.note))

            if event_is_rest:
                return
            else:
                if self.type == EVENT_TYPE_PATCH_TRIGGER:
                    #------------------------------------------------------------------------
                    # Action: Trigger a patch
                    #------------------------------------------------------------------------
                    if not hasattr(self.output_device, "trigger"):
                        raise InvalidEventException("Device %s does not support this kind of event" % self.output_device)
                    params = dict((key, Pattern.value(value)) for key, value in self.params.items())
                    self.output_device.trigger(self.patch, self.trigger_name, self.trigger_value)

        return True