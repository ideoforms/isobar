import os
import mido
import logging
from typing import Optional
from ..output import OutputDevice
from ...exceptions import DeviceNotFoundException
from ...constants import MIDI_CLOCK_TICKS_PER_BEAT

logger = logging.getLogger(__name__)

class MidiOutputDevice (OutputDevice):
    def __init__(self,
                 device_name: Optional[str] = None,
                 send_clock: bool = False,
                 virtual: bool = False):
        """
        Create a MIDI output device.
        Use `isobar.get_midi_output_names()` to query all available devices.

        Args:
            device_name (str): The name of the target device to use.
                               The default MIDI output device name can also be specified
                               with the environmental variable ISOBAR_DEFAULT_MIDI_OUT.
            send_clock (bool): Whether to send clock sync/reset messages.
            virtual (bool):    Whether to create a "virtual" rtmidi device.
        """
        super().__init__()
        try:
            if device_name is None:
                device_name = os.getenv("ISOBAR_DEFAULT_MIDI_OUT")
            self.midi = mido.open_output(device_name, virtual=virtual)
        except (RuntimeError, SystemError, OSError):
            raise DeviceNotFoundException("Could not find MIDI device")
        self.send_clock = send_clock
        logger.info("Opened MIDI output: %s" % self.midi.name)

    def start(self) -> None:
        """
        Sends a MIDI start message to the output device.
        """
        if self.send_clock:
            msg = mido.Message("start")
            self.midi.send(msg)

    def stop(self) -> None:
        """
        Sends a MIDI stop message to the output device.
        """
        if self.send_clock:
            msg = mido.Message("stop")
            self.midi.send(msg)

    def close(self):
        self.midi.close()
        del self.midi

    @property
    def ticks_per_beat(self) -> int:
        """
        The number of clock ticks per beat.
        For MIDI devices, which is fixed at the MIDI standard of 24.
        """
        return MIDI_CLOCK_TICKS_PER_BEAT

    def tick(self) -> None:
        if self.send_clock:
            msg = mido.Message("clock")
            self.midi.send(msg)

    def note_on(self, note: int = 60, velocity: int = 64, channel: int = 0) -> None:
        logger.info("[midi] Note on  (channel = %d, note = %d, velocity = %d)" % (channel, note, velocity))
        msg = mido.Message('note_on', note=int(note), velocity=int(velocity), channel=int(channel))
        self.midi.send(msg)

    def note_off(self, note: int = 60, channel: int = 0) -> None:
        logger.debug("[midi] Note off (channel = %d, note = %d)" % (channel, note))
        msg = mido.Message('note_off', note=int(note), channel=int(channel))
        self.midi.send(msg)

    def all_notes_off(self) -> None:
        logger.debug("[midi] All notes off")
        for channel in range(16):
            for note in range(128):
                msg = mido.Message('note_off', note=int(note), channel=int(channel))
                self.midi.send(msg)

    def control(self, control: int = 0, value: int = 0, channel: int = 0):
        logger.debug("[midi] Control (channel %d, control %d, value %d)" % (channel, control, value))
        msg = mido.Message('control_change', control=int(control), value=int(value), channel=int(channel))
        self.midi.send(msg)

    def program_change(self, program: int = 0, channel: int = 0) -> None:
        logger.debug("[midi] Program change (channel %d, program_change %d)" % (channel, program))
        msg = mido.Message('program_change', program=int(program), channel=int(channel))
        self.midi.send(msg)

    def pitch_bend(self, pitch: int = 0, channel: int = 0) -> None:
        logger.debug("[midi] Pitch bend (channel %d, pitch %d)" % (channel, pitch))
        msg = mido.Message('pitchwheel', pitch=int(pitch), channel=int(channel))
        self.midi.send(msg)

    def aftertouch(self, value: int = 0, channel: int = 0) -> None:
        logger.debug("[midi] Aftertouch (channel %d, pitch %d)" % (channel, value))
        msg = mido.Message('aftertouch', value=int(value), channel=int(channel))
        self.midi.send(msg)

    def set_song_pos(self, pos: int = 0) -> None:
        msg = mido.Message('songpos', pos=pos)
        self.midi.send(msg)

    def __del__(self):
        if hasattr(self, "midi"):
            del self.midi
