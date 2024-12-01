from ..output import OutputDevice
import numpy
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
            value = self.channel_cvs[channel]
            if value is None:
                value = 0.0
            if self.ping_flag[channel]:
                value = 10.0
                self.ping_flag[channel] = False
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
        # Number of channels available
        self.channels = self.stream.channels
        # Channel output CV values
        self.channel_cvs = [None] * self.channels
        # Channel MIDI to CV mappings
        self.channel_map = {}
        # Ping flag
        self.ping_flag = [False] * self.channels

        print("Started CV output with %d channels" % self.channels)

    # TODO: Retrigger event possible?
    # TODO: Add polyphony handling and settings
    def map_channels(self, midi_channel=0, note_channel=None, velocity_channel=None, gate_channel=None):
        """
        Distribute CV outputs from a single MIDI channel.

        Select what channels to output CV data from a number of MIDI properties.

        Args:
            midi_channel (int): MIDI channel to receive data from, commonly set in pattern scheduling
            note_channel (int): CV channel to output note using V/OCT frequency
            velocity_channel (int): CV channel to output note velocity
            gate_channel (int): CV channel to output current gate (10V when open)
        """
        if not all((ch == None or (ch >= 0 and ch <= self.channels)) for ch in [midi_channel, note_channel, velocity_channel, gate_channel]):
            raise ValueError(
                "set_channels: All set channels need to be an integer greater than 0 and less than the channel max (%d)" % self.channels)

        # Mappings in a list of [note, velocity, gate]
        self.channel_map[midi_channel] = [note_channel, velocity_channel, gate_channel]

    def reset_channel(self, midi_channel):
        """
        Reset all CV channel mappings for a given MIDI channel.

        Remove any CV outputs for the given MIDI channel

        Args:
            midi_channel (int): MIDI channel to erase CV channel pairings from
        """
        # Set all outputs to 0
        mappings = self.channel_map.get(midi_channel)
        if (mappings):
            for ch in self.channel_map[midi_channel]:
                self._set_channel_value(ch, None)
            del self.channel_map[midi_channel]
            print("MIDI channel %d mappings removed" % midi_channel)
        else:
            print("No MIDI channel %d mappings found" % midi_channel)

    def print_channels(self):
        """
        Show all currently assigned channels.

        Display all channels that are currently assigned in a tree view
        """
        # Loop through dictionary for outputs
        for midi_channel in self.channel_map:
            # Print MIDI title
            print("MIDI Channel %d" % midi_channel)
            # Use %s in the case of None
            print("\t\\ Note: %s" % self.channel_map[midi_channel][0])
            print("\t\\ Velocity: %s" % self.channel_map[midi_channel][1])
            print("\t\\ Gate: %s" % self.channel_map[midi_channel][2])

    def ping_channel(self, channel):
        """
        Ping an output CV channel to test connection

        Send a 5V signal to a specified channel for 100ms

        Args:
            channel (int): CV channel to output ping
        """
        self.ping_flag[channel] = True

    # TODO: Implement bipolar setting
    def _note_index_to_amplitude(self, note, bipolar=False):
        # Reduce to -5V to 5V if bipolar
        note_float = (note / (12 * self.output_voltage_max)) - (0.5 * bipolar)
        if note_float < -1.0 or note_float > 1.0:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)
        return note_float

    def _set_channel_value(self, channel, cv):
        if cv and (cv < -1.0 or cv > 1.0):
            raise ValueError("CV value %f is outside the voltage range supported by this device" % cv)
        self.channel_cvs[channel] = cv

    def note_on(self, note=60, velocity=64, channel=None):
        note_float = self._note_index_to_amplitude(note)
        print("Note On: %d, CV %f" % (note, note_float))
        # See if the specified MIDI channel exists
        channel_set = self.channel_map.get(channel)
        if (channel_set):
            # Distribute outputs (note, velocity, gate)
            output_cvs = [note_float, (velocity/127), 1.0]
            for ch, cv in zip(channel_set, output_cvs):
                # Make sure the channel is assigned
                if ch is not None:
                    self._set_channel_value(ch, cv)
        # Otherwise select the next open channel
        else:
            for index, channel_note in enumerate(self.channel_cvs):
                if channel_note is None:
                    self._set_channel_value(index, None)
                    break

    def note_off(self, note=60, channel=None):
        # See if the specified MIDI channel exists
        channel_set = self.channel_map.get(channel)
        if (channel_set is not None):
            # Turn all outputs off
            for ch in channel_set:
                if ch is not None:
                    self._set_channel_value(ch, 0)
        # Otherwise select the next open channel
        note_float = self._note_index_to_amplitude(note)
        for index, channel_note in enumerate(self.channel_cvs):
            if channel_note is not None and channel_note == note_float:
                self._set_channel_value(index, None)

    def control(self, control, value, channel=0):
        pass