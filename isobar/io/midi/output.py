import mido
import logging
from ..output import OutputDevice
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiOut (OutputDevice):
    def __init__(self, device_name=None, clock_target=None):
        """
        Create a MIDI output device.

        Args:
            device_name (str): The name of the target device to use.
                               If not specified, uses the system default.
        """
        self.midi = mido.open_output(device_name)
        self.clock_target = clock_target
        log.info("Opened MIDI output: %s" % self.midi.name)

    def tick(self, tick_length):
        if self.clock_target:
            msg = mido.Message('clock')
            self.midi.send(msg)

    def note_on(self, note=60, velocity=64, channel=0):
        log.debug("[midi] Note on  (channel = %d, note = %d, velocity = %d)" % (channel, note, velocity))
        msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
        self.midi.send(msg)

    def note_off(self, note=60, channel=0):
        log.debug("[midi] Note off (channel = %d, note = %d)" % (channel, note))
        msg = mido.Message('note_off', note=note, channel=channel)
        self.midi.send(msg)

    def all_notes_off(self):
        log.debug("[midi] All notes off")
        for channel in range(16):
            for note in range(128):
                msg = mido.Message('note_off', note=note, channel=channel)
                self.midi.send(msg)

    def control(self, control=0, value=0, channel=0):
        log.debug("[midi] Control (channel %d, control %d, value %d)" % (channel, control, value))
        msg = mido.Message('control', control=control, value=value, channel=channel)
        self.midi.send(msg)

    def __destroy__(self):
        del self.midi
