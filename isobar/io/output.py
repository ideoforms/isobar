import logging

log = logging.getLogger(__name__)

class DummyOutputDevice:
    def __init__(self):
        """
        Dummy output device.
        """
        self.current_time = 0.0

    def tick(self, tick_duration):
        self.current_time += tick_duration

    def note_on(self, note=60, velocity=64, channel=0):
        pass

    def note_off(self, note=60, channel=0):
        pass

    def all_notes_off(self, channel=0):
        pass

    def control(self, control=0, value=0, channel=0):
        pass
