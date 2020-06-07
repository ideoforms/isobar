class MidiNote:
    def __init__(self, pitch, velocity, location, duration=None):
        # pitch = MIDI 0..127
        self.pitch = pitch
        # velocity = MIDI 0..127
        self.velocity = velocity
        # location in time, beats
        self.location = location
        # duration in time, beats
        self.duration = duration
