from ..midi.output import MidiOutputDevice
from ...timelines.midi_note import MidiNoteInstance

from typing import Optional

class AbletonMidiOutputDevice (MidiOutputDevice):
    def __init__(self,
                 device_name: Optional[str] = None,
                 send_clock: bool = False,
                 live_set: Optional[object] = None):
        super().__init__(device_name=device_name,
                         send_clock=send_clock)
        
        import live
        self.live_set = live_set
        if self.live_set is None:
            self.live_set = live.Set(scan=True)
                   

    def perform(self, note: MidiNoteInstance) -> None:
        """
        Perform a MIDI note event on the Ableton MIDI output device.

        Args:
            note (MidiNoteInstance): The MIDI note instance to perform.
        """
        # if note.params:
            # Handle additional parameters if needed
            # for param_name, param_value in note.params.items():
        
        self.note_on(note.note, note.amplitude, note.channel)
        if note.params:
            if "live_track" in note.params:
                # May not be present (e.g. if in an echo'd note)
                live_track = note.params["live_track"]
                del note.params["live_track"]
                for key, value in note.params.items():
                    # TODO: This is very inefficient as it has to search the whole list each time
                    #       Make more efficient in pylive with a hashtable
                    try:
                        live_track.devices[0].set_parameter(key, value)
                    except StopIteration:
                        print(f"Warning: Could not find parameter '{key}' in Live device.")
