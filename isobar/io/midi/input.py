try:
    import rtmidi
except:
    print("rtmidi not found, no MIDI support available.")

import time
import logging
from ...note import Note
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiIn:
    def __init__(self, target=None):
        self.midi = rtmidi.MidiIn()

        #------------------------------------------------------------------------
        # don't ignore MIDI clock messages (is on by default)
        #------------------------------------------------------------------------
        self.midi.ignore_types(timing=False)
        self.clock_target = None

        ports = self.midi.get_ports()
        if len(ports) == 0:
            raise DeviceNotFoundException("No MIDI ports found")

        port_index = 0
        if target is not None:
            for index, name in enumerate(ports):
                if name == target:
                    log.info("Found MIDI source (%s)" % name)
                    port_index = index

            if self.midi is None:
                raise DeviceNotFoundException("Could not find MIDI source %s" % target)

        self.midi.open_port(port_index)

    def callback(self, message, timestamp):
        """
        Callback for rtmidi
        Args:
            message: rtmidi message
            timestamp: rtmidi timestamp
        """
        message = message[0]
        data_type = message[0]

        if data_type == 248:
            if self.clock_target is not None:
                self.clock_target.tick()

        elif data_type == 250:
            if self.clock_target is not None:
                self.clock_target.reset_to_beat()

    def run(self):
        """
        Run indefinitely.
        """
        self.midi.set_callback(self.callback)
        while True:
            time.sleep(0.1)

    def poll(self):
        """
        Non-blocking poll for MIDI messages.
        Returns:
            Note: The note received, or None.
        """
        message = self.midi.get_message()
        if not message:
            return

        try:
            data_type, data_note, data_vel = message[0]

            if (data_type & 0x90) > 0 and data_vel > 0:
                # note on
                return Note(data_note, data_vel)
        except:
            pass

    def close(self):
        del self.midi