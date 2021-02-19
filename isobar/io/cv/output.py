from ..output import OutputDevice

try:
    import sounddevice
except ModuleNotFoundError:
    pass

def get_cv_output_devices():
    return list(sounddevice.query_devices())

class CVOutputDevice(OutputDevice):
    """
    CVOutputDevice: Sends output to CV over an audio I/O device.
    """

    def audio_callback(self, out_data, frames, time, status):
        for channel in range(self.channels):
            value = self.channel_notes[channel]
            if value is None:
                value = 0.0
            out_data[:, channel] = value

    def __init__(self, device_name=None, sample_rate=44100):
        """
        Create a control voltage output device.

        Control voltage signals require a DC-coupled audio interface, which Python
        sends audio signals to via the sounddevice library. 

        Args:
            device_name (str): Name of the audio output device to use.
                               To query possible names, call get_cv_output_devices().
            sample_rate (int): Audio sample rate to use.
        """
        try:
            self.stream = sounddevice.OutputStream(device=device_name,
                                                   samplerate=sample_rate,
                                                   dtype="float32",
                                                   callback=self.audio_callback)
            self.stream.start()

        except NameError:
            raise Exception("For CV support, the sounddevice module must be installed")

        # Expert Sleepers ES-8 supports entire -10V to +10V range
        self.output_voltage_max = 10
        self.channels = self.stream.channels
        self.channel_notes = [None] * self.channels
        self.middle_c = 60

        print("Started CV output with %d channels" % self.channels)

    def _note_index_to_amplitude(self, note):
        note_float = (note - self.middle_c) / (12 * self.output_voltage_max)
        if note_float < -1.0 or note_float > 1.0:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)
        print("note %d, float %f" % (note, note_float))
        return note_float

    def note_on(self, note=60, velocity=64, channel=0):
        note_float = self._note_index_to_amplitude(note)
        for index, channel_note in enumerate(self.channel_notes):
            if channel_note is None:
                self.channel_notes[index] = note_float
                break

    def note_off(self, note=60, channel=0):
        note_float = self._note_index_to_amplitude(note)
        for index, channel_note in enumerate(self.channel_notes):
            if channel_note is not None and channel_note == note_float:
                self.channel_notes[index] = None

    def control(self, control, value, channel=0):
        pass
