try:
    import rtmidi
except:
    print("rtmidi not found, no MIDI support available.")

import logging
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiOut:
    def __init__(self, device_name=None):
        """
        Create a MIDI output device.

        Args:
            device_name (str): The name of the target device to use.
                               If not specified, uses the system default.
        """
        self.midi = rtmidi.MidiOut()

        ports = self.midi.get_ports()
        if len(ports) == 0:
            raise DeviceNotFoundException("No MIDI output ports found")

        port_index = 0
        if device_name is not None:
            for index, name in enumerate(ports):
                if name == device_name:
                    log.info("Found MIDI output (%s)" % name)
                    port_index = index

            if self.midi is None:
                raise DeviceNotFoundException("Could not find MIDI target %s" % target)

        self.midi.open_port(port_index)
        port_name = self.midi.get_port_name(port_index)
        log.info("Opened MIDI output: %s" % port_name)

    def tick(self, tick_length):
        pass

    def note_on(self, note=60, velocity=64, channel=0):
        log.debug("[midi] Note on  (channel = %d, note = %d, velocity = %d)" % (channel, note, velocity))
        self.midi.send_message([0x90 + channel, int(note), int(velocity)])

    def note_off(self, note=60, channel=0):
        log.debug("[midi] Note off (channel = %d, note = %d)" % (channel, note))
        self.midi.send_message([0x80 + channel, int(note), 0])

    def all_notes_off(self, channel=0):
        log.debug("[midi] All notes off (channel = %d)" % (channel))
        for n in range(128):
            self.note_off(n, channel)

    def control(self, control=0, value=0, channel=0):
        log.debug("[midi] Control (channel %d, control %d, value %d)" % (channel, control, value))
        self.midi.send_message([0xB0 + channel, int(control), int(value)])

    def __destroy__(self):
        del self.midi