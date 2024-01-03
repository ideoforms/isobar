"""
MIDI control: Patterns which generate their outputs based on MIDI devices.
"""

from .core import Pattern

from typing import Optional
import mido
import os

class IsobarMIDIManager:
    shared_manager = None

    def __init__(self, device_name: str = None):
        if device_name is None:
            if os.getenv("ISOBAR_DEFAULT_MIDI_IN") is not None:
                device_name = os.getenv("ISOBAR_DEFAULT_MIDI_IN")

        self.input = mido.open_input(device_name)
        self.input.callback = self.handle_message
        self.control_handlers = [[] for _ in range(128)]

        if IsobarMIDIManager.shared_manager is None:
            IsobarMIDIManager.shared_manager = self

    def handle_message(self, message):
        if message.type == 'control_change':
            self.on_control_change(message.control, message.value)

    @classmethod
    def get_shared_manager(cls):
        if IsobarMIDIManager.shared_manager is None:
            IsobarMIDIManager.shared_manager = IsobarMIDIManager()
        return IsobarMIDIManager.shared_manager

    def add_control_handler(self, control, handler):
        self.control_handlers[control].append(handler)

    def on_control_change(self, control, value):
        for handler in self.control_handlers[control]:
            handler.on_change(value)

class PMIDIControl(Pattern):
    def __init__(self, control_index: int = 0, normalized: bool = False, default: int = None):
        self.control_index: int = control_index
        self.value: Optional[int] = default
        self.normalized: bool = normalized

        manager = IsobarMIDIManager.get_shared_manager()
        manager.add_control_handler(self.control_index, self)

    def __str__(self):
        classname = str(self.pattern.__class__).split(".")[-1]
        return "%s(%s)" % (classname, str(self.pattern))

    def __next__(self):
        return self.value

    def on_change(self, value: int):
        if self.normalized:
            self.value = value / 127
        else:
            self.value = value
