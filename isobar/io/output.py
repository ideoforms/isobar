import logging

log = logging.getLogger(__name__)

class OutputDevice:
    def __init__(self):
        pass

    def tick(self, tick_duration):
        pass

    def note_on(self, note=60, velocity=64, channel=0):
        pass

    def note_off(self, note=60, channel=0):
        pass

    def control(self, control=0, value=0, channel=0):
        pass
