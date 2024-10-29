import logging

log = logging.getLogger(__name__)

class OutputDevice:
    def __init__(self):
        self.added_latency_seconds = 0.0
        """ added_latency_seconds can be used to compensate for latency offsets between output
        devices. It is preferable to using timeline.defaults.delay as it is measured in seconds,
        whereas timeline.defaults.delay is in beats and so varies by BPM. """
    
    def __str__(self):  
        return "Device (%s)" % (self.__class__.__name__)

    @property
    def ticks_per_beat(self):
        return None

    def tick(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def note_on(self, note=60, velocity=64, channel=0):
        pass

    def note_off(self, note=60, channel=0):
        pass

    def all_notes_off(self):
        for channel in range(16):
            for note_index in range(128):
                self.note_off(note_index, channel=channel)

    def control(self, control=0, value=0, channel=0):
        pass

    def program_change(self, program=0, channel=0):
        pass
