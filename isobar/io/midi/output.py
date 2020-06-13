import os
import mido
import logging
from ..output import OutputDevice
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiOut (OutputDevice):
    def __init__(self, device_name=None, send_clock=False):
        """
        Create a MIDI output device.

        Args:
            device_name (str): The name of the target device to use.
                               The default MIDI output device name can also be specified
                               with the environmental variable ISOBAR_DEFAULT_MIDI_OUT.
            send_clock (bool): Whether to send clock sync/reset messages.
        """
        try:
            if device_name is None:
                device_name = os.getenv("ISOBAR_DEFAULT_MIDI_OUT")
            self.midi = mido.open_output(device_name)
        except (RuntimeError, SystemError, OSError):
            raise DeviceNotFoundException("Could not find MIDI device")
        self.send_clock = send_clock
        log.info("Opened MIDI output: %s" % self.midi.name)

    def start(self):
        if self.send_clock:
            msg = mido.Message("start")
            self.midi.send(msg)

    def stop(self):
        if self.send_clock:
            msg = mido.Message("stop")
            self.midi.send(msg)

    def tick(self, tick_length):
        if self.send_clock:
            msg = mido.Message("clock")
            self.midi.send(msg)

    def note_on(self, note=60, velocity=64, channel=0):
        log.debug("[midi] Note on  (channel = %d, note = %d, velocity = %d)" % (channel, note, velocity))
        msg = mido.Message('note_on', note=int(note), velocity=int(velocity), channel=int(channel))
        self.midi.send(msg)

    def note_off(self, note=60, channel=0):
        log.debug("[midi] Note off (channel = %d, note = %d)" % (channel, note))
        msg = mido.Message('note_off', note=int(note), channel=int(channel))
        self.midi.send(msg)

    def all_notes_off(self):
        log.debug("[midi] All notes off")
        for channel in range(16):
            for note in range(128):
                msg = mido.Message('note_off', note=int(note), channel=int(channel))
                self.midi.send(msg)

    def control(self, control=0, value=0, channel=0):
        log.debug("[midi] Control (channel %d, control %d, value %d)" % (channel, control, value))
        msg = mido.Message('control', control=int(control), value=int(value), channel=int(channel))
        self.midi.send(msg)

    def __destroy__(self):
        del self.midi
