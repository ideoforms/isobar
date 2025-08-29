from typing import Optional

from ..midi.output import MidiOutputDevice
from .note import MPENote

class MPEOutputDevice (MidiOutputDevice):
    def __init__(self,
                 device_name: Optional[str] = None,
                 send_clock: bool = False,
                 virtual: bool = False):
        """
        Create an MPE output device. 

        New notes are automatically assigned to an unused MIDI channel.

        When `note_on` is called, an `MPENote` object is returned, which can be used
        to control per-note polyphonic expression:

            output_device = MPEOutputDevice()
            note = output_device.note_on(60)
            note.aftertouch(value=64)
            note.pitch_bend(pitch=100)
            note.control(control=74, value=127)
            note.note_off()

        Use `isobar.get_midi_output_names()` to query all available devices.

        Args:
            device_name (str): The name of the target device to use.
                               The default MIDI output device name can also be specified
                               with the environmental variable ISOBAR_DEFAULT_MIDI_OUT.
            send_clock (bool): Whether to send clock sync/reset messages.
            virtual (bool):    Whether to create a "virtual" rtmidi device.
        """
        super().__init__(device_name, send_clock, virtual)

        self.channels = list(range(1, 16))
        self.note_assignments = dict((n, MPENote) for n in range(128))
        self.channel_assignments: dict[int, MPENote] = dict((n, None) for n in self.channels)
    
    def _get_next_channel(self) -> Optional[int]:
        """
        Return the next unused MIDI channel, or None if no channels are available.

        Returns:
            Optional[int]: The channel index.
        """
        for channel in self.channels:
            if self.channel_assignments[channel] is None:
                return channel
        return None
    
    def note_on(self,
                note_index: int,
                velocity: int) -> MPENote:
        channel = self._get_next_channel()
        if channel is None:
            # No channels are available
            return None
        else:
            note = MPENote(note=note_index,
                           channel=channel,
                           output_device=self)
            
            self.note_assignments[note_index] = note
            self.channel_assignments[channel] = note

            super().note_on(note_index, velocity, channel)
            return note
    
    def note_off(self,
                 note_index: int):
        note = self.note_assignments[note_index]
        if note is None:
            raise ValueError("MPE: note_off received for non-depressed note (%d)" % note_index)
        else:
            super().note_off(note_index, note.channel)
            self.channel_assignments[note_index] = None
            self.note_assignments[note_index] = None
            note.is_down = False