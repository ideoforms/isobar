import mido

import time
import queue
import logging
from ...note import Note
from ...exceptions import DeviceNotFoundException

log = logging.getLogger(__name__)

class MidiIn:
    def __init__(self, device_name=None):
        try:
            self.midi = mido.open_input(device_name, callback=self.callback)
        except (RuntimeError, SystemError):
            raise DeviceNotFoundException("Could not find MIDI device")

        self.clock_target = None
        self.queue = queue.Queue()
        self.estimated_tempo = None
        self.last_clock_time = None
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
            if self.last_clock_time is not None:
                dt = time.time() - self.last_clock_time
                tick_estimate = (120/48) * 1.0/dt
                if self.estimated_tempo is None:
                    self.estimated_tempo = tick_estimate
                else:
                    smoothing = 0.95
                    self.estimated_tempo = (smoothing * self.estimated_tempo) + ((1.0 - smoothing) * tick_estimate)
                self.last_clock_time = time.time()
            else:
                self.last_clock_time = time.time()

            if self.clock_target is not None:
                self.clock_target.tick()

        elif message.type == 'reset':
            log.info("MIDI reset received")
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
    def tempo(self):
        return self.estimated_tempo

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
