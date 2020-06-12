import mido

import time
import queue
import logging
from ...note import Note
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiIn:
    def __init__(self, device_name=None):
        self.midi = mido.open_input(device_name, callback=self.callback)
        self.clock_target = None
        self.queue = queue.Queue()
        log.info("Opened MIDI input: %s" % self.midi.name)

    @property
    def device_name(self):
        return self.midi.name

    def callback(self, message):
        """
        Callback for mido
        Args:
            message (mido.Message): The message
        """
        log.debug(" - MIDI message received: %s" % message)

        if message.type == 'clock':
            if self.clock_target is not None:
                self.clock_target.tick()

        elif message.type == 'reset':
            if self.clock_target is not None:
                self.clock_target.reset_to_beat()

        elif message.type == 'note_on' or message.type == 'control':
            self.queue.put(message)

    def run(self):
        """
        Run indefinitely.
        """
        while True:
            time.sleep(0.1)

    @property
    def bpm(self):
        return None

    def receive(self):
        return self.queue.get()

    def poll(self):
        """
        Non-blocking poll for MIDI messages.
        Returns:
            Note: The note received, or None.
        """
        rv = None
        try:
            rv = self.queue.get_nowait()
        except queue.Empty:
            pass
        return rv

    def close(self):
        del self.midi
