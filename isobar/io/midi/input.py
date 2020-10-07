import mido

import os
import time
import queue
import logging
from ...exceptions import DeviceNotFoundException
from ...constants import MIDI_CLOCK_TICKS_PER_BEAT

log = logging.getLogger(__name__)

class MidiInputDevice:
    def __init__(self, device_name=None, clock_target=None, virtual=False):
        """
        Create a MIDI input device.
        Use `isobar.get_midi_input_names()` to query all available devices.

        Args:
            device_name (str): The name of the target device to use.
                               The default MIDI output device name can also be specified
                               with the environmental variable ISOBAR_DEFAULT_MIDI_IN.
            clock_target:      Target to send clocking events to. To sync a specific
                               Timeline to a MidiInputDevice device, use
                               `timeline.clock_source = midi_in`.
            virtual (bool):    Whether to create a "virtual" rtmidi device.
        """
        if device_name is None:
            device_name = os.getenv("ISOBAR_DEFAULT_MIDI_IN")
        try:
            self.midi = mido.open_input(device_name, callback=self._callback, virtual=virtual)
        except (RuntimeError, SystemError, OSError):
            raise DeviceNotFoundException("Could not find MIDI device")

        self.clock_target = clock_target
        self.queue = queue.Queue()
        self.callback = None
        self.estimated_tempo = None
        self.last_clock_time = None
        log.info("Opened MIDI input: %s" % self.midi.name)

    @property
    def device_name(self):
        return self.midi.name

    def _callback(self, message):
        """
        Callback used by mido.
        Args:
            message: A mido.Message.
        """
        log.debug(" - MIDI message received: %s" % message)

        if message.type == 'clock':
            if self.last_clock_time is not None:
                dt = time.time() - self.last_clock_time
                tick_estimate = (120 / 48) * 1.0 / dt
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

        elif message.type == 'start':
            log.info(" - MIDI: Received start message")
            if self.clock_target is not None:
                self.clock_target.start()

        elif message.type == 'stop':
            log.info(" - MIDI: Received stop message")
            if self.clock_target is not None:
                self.clock_target.stop()

        elif message.type == 'songpos':
            log.info(" - MIDI: Received songpos message")
            if message.pos == 0:
                if self.clock_target is not None:
                    self.clock_target.reset()
            else:
                log.warning("MIDI song position message received, but MIDI input cannot seek to arbitrary position")

        elif message.type in ['note_on', 'note_off', 'control_change', 'pitchwheel']:
            if self.callback:
                self.callback(message)
            else:
                self.queue.put(message)

    def stop(self):
        pass

    def run(self):
        """
        Run indefinitely.
        """
        while True:
            time.sleep(0.1)

    def get_tempo(self):
        return self.estimated_tempo

    def set_tempo(self, tempo):
        raise RuntimeError("Cannot set the tempo of an external clock")

    tempo = property(get_tempo, set_tempo)

    @property
    def ticks_per_beat(self):
        return MIDI_CLOCK_TICKS_PER_BEAT

    def receive(self):
        """
        Return the next MIDI event, blocking until an event is received.

        Returns a mido Message object:
        https://mido.readthedocs.io/en/latest/messages.html

        Messages may be of type note, control_change, program_change, pitch_bend.

        Returns:
            Message: The event received, or None.
        """
        return self.queue.get()

    def poll(self):
        """
        Similar to `receive`, but does not block. If an event has been received,
        it returns the mido Message immediately. Otherwise, returns None.

        Returns:
            Message: The event received, or None.
        """
        rv = None
        try:
            rv = self.queue.get_nowait()
        except queue.Empty:
            pass
        return rv

    def close(self):
        del self.midi
