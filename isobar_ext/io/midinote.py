class MidiNote:
    def __init__(self, pitch, velocity, location, channel=0, duration=None):
        # channel = 0..15
        self.channel = channel
        # pitch = MIDI 0..127
        self.pitch = pitch
        # velocity = MIDI 0..127
        self.velocity = velocity
        # location in time, beats
        self.location = location
        # duration in time, beats
        self.duration = duration

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Invalid channel value. Channel must be between 0 and 15.")
        self._channel = value

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        if not 0 <= value <= 127:
            raise ValueError("Invalid pitch value. Pitch must be between 0 and 127.")
        self._pitch = value

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        if not 0 <= value <= 127:
            raise ValueError("Invalid velocity value. Velocity must be between 0 and 127.")
        self._velocity = value

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        if value is not None and value < 0:
            raise ValueError("Invalid duration value. Duration must be a non-negative number.")
        self._duration = value

