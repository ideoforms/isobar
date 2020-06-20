import logging
from ..output import OutputDevice
from ...constants import DEFAULT_TICKS_PER_BEAT

log = logging.getLogger(__name__)

class DummyOutputDevice(OutputDevice):
    def __init__(self):
        """
        Dummy output device.
        """
        self.current_time = 0.0
        self.events = []

    @property
    def ticks_per_beat(self):
        return DEFAULT_TICKS_PER_BEAT

    def tick(self):
        self.current_time += 1.0 / self.ticks_per_beat

    def note_on(self, note=60, velocity=64, channel=0):
        self.events.append([round(self.current_time, 8), "note_on", note, velocity, channel])

    def note_off(self, note=60, channel=0):
        self.events.append([round(self.current_time, 8), "note_off", note, channel])

    def control(self, control=0, value=0, channel=0):
        self.events.append([round(self.current_time, 8), "control", control, value, channel])
