from ..output import OutputDevice
import time

def get_cv_output_devices():
    try:
        import sounddevice
    except ModuleNotFoundError:
        raise RuntimeError(
            "get_cv_output_devices: Couldn't import the sounddevice module (to install: pip3 install sounddevice)")
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
        super().__init__()

        #--------------------------------------------------------------------------------
        # Lazily import sounddevice, to avoid the additional time cost of initializing
        # PortAudio when not needed
        #--------------------------------------------------------------------------------
        try:
            import sounddevice
            import numpy as np
        except ModuleNotFoundError:
            raise RuntimeError(
                "CVOutputDevice: Couldn't import the sounddevice or numpy modules (to install: pip3 install sounddevice numpy)")

        try:
            self.stream = sounddevice.OutputStream(device=device_name,
                                                   samplerate=sample_rate,
                                                   dtype="float32",
                                                   callback=self.audio_callback)
            self.stream.start()

        except NameError:
            raise Exception("For CV support, the sounddevice and numpy modules must be installed")

        # Expert Sleepers ES-8 supports entire -10V to +10V range
        self.output_voltage_max = 10
        self.channels = self.stream.channels
        self.channel_notes = [None] * self.channels
        self.channel_map = [None] * self.channels

        print("Started CV output with %d channels" % self.channels)

    # TODO: Retrigger event possible?
    def set_channels(self, midi_channel=0, note_channel=None, velocity_channel=None, gate_channel=None):
        """
        Distribute CV outputs from a single MIDI channel.

        Select what channels to output CV data from a number of MIDI properties.

        Args:
            midi_channel (int): MIDI channel to receive data from, commonly set in pattern scheduling
            note_channel (int): CV channel to output note using V/OCT frequency
            velocity_channel (int): CV channel to output note velocity
            gate_channel (int): CV channel to output current gate (10V when open)
        """
        if not all((ch == None or ch >= 0) for ch in [midi_channel, note_channel, velocity_channel, gate_channel]):
            print("set_channels: All set channels need to be an integer greater than 0")

        # Mappings in a list of [note, velocity, gate]
        self.channel_map[midi_channel] = [note_channel, velocity_channel, gate_channel]

    def reset_channel(self, midi_channel):
        """
        Reset all CV channel mappings for a given MIDI channel.

        Remove any CV outputs for the given MIDI channel

        Args:
            midi_channel (int): MIDI channel to erase CV channel pairings from
        """
        self.channel_map[midi_channel] = None

    def show_channels(self):
        """
        Show all currently assigned channels.

        Display all channels that are currently assigned in a tree view
        """

    def ping_channel(self, channel):
        """
        Ping an output CV channel to test connection

        Send a 5V signal to a specified channel for 100ms

        Args:
            channel (int): CV channel to output ping
        """
        self.note_on(channel=channel)
        time.sleep(0.1)
        self.note_off(channel=channel)

    # TODO: Implement bipolar setting
    def _note_index_to_amplitude(self, note, bipolar=False):
        # Reduce to -5V to 5V if bipolar
        note_float = (note / (12 * self.output_voltage_max)) - (0.5 * bipolar)
        if note_float < -1.0 or note_float > 1.0:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)
        print("note %d, float %f" % (note, note_float))
        print(12 * self.output_voltage_max)
        return note_float

    def note_on(self, note=60, velocity=64, channel=None):
        note_float = self._note_index_to_amplitude(note)
        # See if the specified MIDI channel exists
        channel_set = self.channel_map[channel]
        if (channel_set is not None):
            # Distribute outputs (note, velocity, gate)
            output_cvs = [note_float, (velocity/127), 1.0]
            for i in range(len(channel_set)):
                self.channel_notes[channel_set[i]] = output_cvs[i]
        # Otherwise select the next open channel
        else:
            for index, channel_note in enumerate(self.channel_notes):
                if channel_note is None:
                    self.channel_notes[index] = note_float
                    break

    def note_off(self, note=60, channel=None):
        # See if the specified MIDI channel exists
        channel_set = self.channel_map[channel]
        if (channel_set is not None):
            # Turn all outputs off
            for i in range(len(channel_set)):
                self.channel_notes[channel_set[i]] = 0
        # Otherwise select the next open channel
        note_float = self._note_index_to_amplitude(note)
        for index, channel_note in enumerate(self.channel_notes):
            if channel_note is not None and channel_note == note_float:
                self.channel_notes[index] = None

    def control(self, control, value, channel=0):
        pass