from ..output import OutputDevice
from enum import Enum

def get_cv_output_devices():
    """
    Show all available CV output device names
    """
    try:
        import sounddevice
    except ModuleNotFoundError:
        raise RuntimeError(
            "get_cv_output_devices: Couldn't import the sounddevice module (to install: pip3 install sounddevice)")
    return list(sounddevice.query_devices())

class CVPolyMode(Enum):
    """
    Setting for how to handle polyphony in CV output
    """
    NEXT = 0
    HIGHEST = 1
    LOWEST = 2

class CVMapping():
    """
    Map MIDI channels to CV channels
    """
    # Which MIDI channel is this for
    midi = None
    # Which poly mode should be used (see CVPolyModes Enum)
    poly_mode = None

    # Dictionary of all mapped CV channels
    channels = {
        'note': None,
        'velocity': None,
        'gate': None,
        'trigger': None,
    }

    def __init__(self, max_channels=0, midi_channel=None, note_channel=None, velocity_channel=None, gate_channel=None, trigger_channel=None,
                 poly_channels=[], poly_mode=0):
        """
        Declare a MIDI to CV channel mapping set. Also allows for custom CV parameter setting

        Args:
            max_channels: Maximum channels available from the current CV output
            midi_channel: MIDI channel to take MIDI input from
            note_channel: CV channel to output note data
            velocity_channel: CV channel to output velocity data
            gate_channel: CV channel to output gate data (max voltage when note is on, 0 when note is off)
            trigger_channel: CV channel to output trigger data (max voltage ping whenever note is on)
            poly_channels: CV channels to output multiple notes at once
            poly_mode: How to distribute multiple notes being played at once, using the CVPolyMode Enum
        """
        # Validate input channels
        if not all((ch == None or (ch >= 0 and ch <= max_channels)) for ch in [midi_channel, note_channel, velocity_channel, gate_channel, trigger_channel]):
            raise ValueError(
                "set_channels: All set channels need to be an integer greater than 0 and less than the channel max (%d)" % max_channels)
        if poly_channels and all((ch >= 0 and ch <= max_channels) for ch in poly_channels):
            raise ValueError(
                "set_channels: All poly channels need to be an integer greater than 0 and less than the channel max (%d)" % max_channels)
        self.midi = midi_channel
        self.channels['note'] = note_channel
        self.channels['velocity'] = velocity_channel
        self.channels['gate'] = gate_channel
        self.channels['trigger'] = trigger_channel
        self.poly_mode = poly_mode

    def __str__(self):
        # Store output
        outstr = ""
        outstr += ("MIDI Channel %d\n" % self.midi)
        # Use %s in the case of None
        outstr += ("\t\\ Note: %s\n" % self.channels['note'])
        outstr += ("\t\\ Velocity: %s\n" % self.channels['velocity'])
        outstr += ("\t\\ Gate: %s\n" % self.channels['gate'])
        outstr += ("\t\\ Trigger: %s\n" % self.channels['trigger'])
        return outstr

    def get_output_channels(self, note=None, velocity=None, gate=None):
        """
        Return a tuple list of channel numbers and given CV outputs to easily set multiple output values at once

        Args:
            note: CV output for the note channel
            velocity: CV output for the velocity channel
            gate: CV output for the gate channel
            trigger: CV output for the trigger channel
        """
        # Iterate through channel dictionary
        channel_pairs = []
        # Return the pair of channel ID and note value if the CV output and channel exists
        if self.channels['note'] is not None and note is not None:
            channel_pairs.append([self.channels['note'], note])
        if self.channels['velocity'] is not None and velocity is not None:
            channel_pairs.append([self.channels['velocity'], velocity])
        if self.channels['gate'] is not None and gate is not None:
            channel_pairs.append([self.channels['gate'], gate])
        return channel_pairs


class CVOutputDevice(OutputDevice):
    """
    Sends output to CV over an audio I/O device.
    """

    def audio_callback(self, out_data, frames, time, status):
        for channel in range(self.channels):
            value = self.channel_cvs[channel]
            if value is None:
                value = 0.0
            if self.ping_flag[channel]:
                value = self.output_voltage_max
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
        # NOTE: Voltage is on a 10x scale, so 1 = 10V
        self.output_voltage_max = 1
        # Number of channels available
        self.channels = self.stream.channels
        # Channel output CV values
        self.channel_cvs = [None] * self.channels
        # Channel MIDI to CV mappings
        self.channel_maps = {}
        # Ping flag
        self.ping_flag = [False] * self.channels

        print("Started CV output with %d channels" % self.channels)

    def set_output_voltage_max(self, voltage):
        """
        Set the max voltage output for this CV output

        Args:
            voltage: Voltage value (commonly from 5V to 10V)
        """
        self.output_voltage_max = voltage/10

    # TODO: Retrigger event possible?
    # Yes it is! Look @ ping event
    # TODO: Add polyphony handling and settings
    def map_channels(self, midi_channel=0, note_channel=None, velocity_channel=None, gate_channel=None, trigger_channel=None, poly_channels=None, poly_setting=None):
        """
        Distribute CV outputs from a single MIDI channel.

        Select what channels to output CV data from a number of MIDI properties.

        Args:
            midi_channel (int): MIDI channel to receive data from, commonly set in pattern scheduling
            note_channel (int): CV channel to output note using V/OCT frequency
            velocity_channel (int): CV channel to output note velocity
            gate_channel (int): CV channel to output current gate (10V when open)
        """
        if not all((ch == None or (ch >= 0 and ch <= self.channels)) for ch in [midi_channel, note_channel, velocity_channel, gate_channel, trigger_channel]):
            raise ValueError(
                "set_channels: All set channels need to be an integer greater than 0 and less than the channel max (%d)" % self.channels)

        # Create an object
        self.channel_maps[midi_channel] = CVMapping(
            self.channels, midi_channel, note_channel, velocity_channel, gate_channel, trigger_channel, poly_channels, poly_setting)

    def reset_channel(self, midi_channel):
        """
        Reset all CV channel mappings for a given MIDI channel.

        Remove any CV outputs for the given MIDI channel

        Args:
            midi_channel (int): MIDI channel to erase CV channel pairings from
        """
        # Set all outputs to 0
        mappings = self.channel_maps.get(midi_channel)
        if (mappings):
            for ch in self.channel_maps[midi_channel].channels.values():
                self._set_channel_value(ch, None)
            del self.channel_maps[midi_channel]
            print("MIDI channel %d mappings removed" % midi_channel)
        else:
            print("No MIDI channel %d mappings found" % midi_channel)

    def print_channels(self):
        """
        Show all currently assigned channels.

        Display all channels that are currently assigned in a tree view
        """
        # Loop through dictionary for outputs
        for cvmap in self.channel_maps.values():
            # Print MIDI title
            print(cvmap)

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
        note_float = (note / 120) - (0.5 * bipolar)
        if note_float < -self.output_voltage_max or note_float > self.output_voltage_max:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)
        return note_float

    def _set_channel_value(self, channel, cv):
        if cv and (cv < -self.output_voltage_max or cv > self.output_voltage_max):
            raise ValueError("CV value %f is outside the voltage range set or supported by this device (%fV)" %
                             (cv, self.output_voltage_max * 10))
        print("Ch: %s, V: %s" % (channel, cv))
        self.channel_cvs[channel] = cv

    def note_on(self, note=60, velocity=64, channel=None):
        note_float = self._note_index_to_amplitude(note)
        print("Note On: %d, CV %f" % (note, note_float))
        # See if the specified MIDI channel exists
        cmap = self.channel_maps.get(channel)
        if (cmap):
            # Check if the trigger channel exists
            triggerChannel = cmap.channels['trigger']
            if triggerChannel:
                # If so, set the flag
                self.ping_flag[triggerChannel] = True
            # Distribute outputs (note, velocity, gate)
            for chcv in cmap.get_output_channels(note_float, (velocity/127) * self.output_voltage_max, self.output_voltage_max):
                self._set_channel_value(chcv[0], chcv[1])
        # Otherwise select the next open channel
        else:
            for index, channel_note in enumerate(self.channel_cvs):
                if channel_note is None:
                    self._set_channel_value(index, None)
                    break

    def note_off(self, note=60, channel=None):
        # See if the specified MIDI channel exists
        cmap = self.channel_maps.get(channel)
        if (cmap is not None):
            # Turn all outputs off
            for chcv in cmap.get_output_channels(0, 0, 0):
                self._set_channel_value(chcv[0], chcv[1])
        # Otherwise select the next open channel
        else:
            note_float = self._note_index_to_amplitude(note)
            for index, channel_note in enumerate(self.channel_cvs):
                if channel_note is not None and channel_note == note_float:
                    self._set_channel_value(index, None)

    def control(self, control, value, channel=0):
        pass