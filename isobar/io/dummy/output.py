import logging
from ..output import OutputDevice

log = logging.getLogger(__name__)

class DummyOutputDevice(OutputDevice):
    def __init__(self):
        """
        Dummy output device.
        """
        self.current_time = 0.0
        self.events = []

    def tick(self, tick_duration):
        self.current_time += tick_duration

    def note_on(self, note=60, velocity=64, channel=0):
        self.events.append([round(self.current_time, 8), "note_on", note, velocity, channel])

    def note_off(self, note=60, channel=0):
        self.events.append([round(self.current_time, 8), "note_off", note, channel])

    def control(self, control=0, value=0, channel=0):
        self.events.append([round(self.current_time, 8), "control", value, channel])
