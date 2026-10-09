from ..output import OutputDevice


def get_cv_output_devices():
    import sounddevice
    return list(sounddevice.query_devices())

class CVChannelMapping:
    def __init__(self,
                 channel_index: int,
                 property_name: str):

        if property_name not in ["note", "gate", "velocity", "clock"]:
            raise ValueError("Invalid property_name: %s" % property_name)

        self.channel_index = channel_index
        self.property_name = property_name

class CVChannelMappings:
    def __init__(self, mappings: list[CVChannelMapping] = []):
        self.mappings = mappings.copy()

        # Note stealing mode. Might consider: last, highest, lowest, random, none
        self.note_priority = "last"

        # Maximum number of simultaneous notes
        self.polyphony = 4

    def add_mapping(self, mapping: CVChannelMapping):
        self.mappings.append(mapping)

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

    def __init__(self,
                 device_name: str = None,
                 sample_rate: int = 44100,
                 channel_mappings: CVChannelMappings = None):
        """
        Create a control voltage output device.

        Control voltage signals require a DC-coupled audio interface, which Python
        sends audio signals to via the sounddevice library. 

        Args:
            device_name (str): Name of the audio output device to use.
                               To query possible names, call get_cv_output_devices().
            sample_rate (int): Audio sample rate to use.
            channel_mappings (CVChannelMappings): Mapping of CV channels to properties (note, gate, velocity, clock).
        """
        super().__init__()

        self.channel_mappings = channel_mappings
        if channel_mappings is None:
            self.channel_mappings = CVChannelMappings()

        #--------------------------------------------------------------------------------
        # Lazily import sounddevice, to avoid the additional time cost of initializing
        # PortAudio when not needed
        #--------------------------------------------------------------------------------
        try:
            import sounddevice
            import numpy as np
        except ModuleNotFoundError:
            raise RuntimeError("CVOutputDevice: Couldn't import the sounddevice or numpy modules (to install: pip3 install sounddevice numpy)")

        try:
            self.stream = sounddevice.OutputStream(device=device_name,
                                                   samplerate=sample_rate,
                                                   blocksize=256,
                                                   dtype="float32",
                                                   callback=self.audio_callback)
            self.stream.start()

        except NameError:
            raise Exception("For CV support, the sounddevice and numpy modules must be installed")

        # Expert Sleepers ES-8 supports entire -10V to +10V range
        self.output_voltage_max = 10
        self.channels = self.stream.channels
        self.channel_notes = [None] * self.channels
        self.midi_note_base = 60

        print("Started CV output with %d channels" % self.channels)

    def _note_index_to_amplitude(self, note):
        note_float = (note - self.midi_note_base) / (12 * self.output_voltage_max)
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
