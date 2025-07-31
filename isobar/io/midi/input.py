import os
import mido
import time
import queue
import logging
from typing import Any, Callable
from ...exceptions import DeviceNotFoundException
from ...constants import MIDI_CLOCK_TICKS_PER_BEAT
from ..midinote import MidiNote

logger = logging.getLogger(__name__)

class MidiInputDevice:
    def __init__(self, 
                 device_name: str = None,
                 clock_target: Any = None,
                 virtual: bool = False):
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
            self.midi = mido.open_input(name=device_name,
                                        callback=self._mido_callback,
                                        virtual=virtual)
        except (RuntimeError, SystemError, OSError):
            raise DeviceNotFoundException("Could not find MIDI device")

        self.clock_target = clock_target
        self.queue = queue.Queue()
        self.estimated_tempo = None
        self.last_clock_time = None

        logger.info("Opened MIDI input: %s" % self.midi.name)

        self.notes_down: list[MidiNote] = []
        self.notes_down_dict: dict[int, MidiNote] = dict((n, None) for n in range(128))

        self.callback: Callable = None
        self.on_note_on_handler: Callable = None
        self.on_note_off_handler: Callable = None
        self.on_control_change_handler: Callable = None
        self.on_aftertouch_handler: Callable = None
        self.on_polytouch_handler: Callable = None
        self.on_pitchbend_handler: Callable = None

    @property
    def device_name(self):
        return self.midi.name

    def _mido_callback(self, message):
        """
        Callback used by mido.
        Args:
            message: A mido.Message.
        """
        logger.debug(" - MIDI message received: %s" % message)

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
            logger.info(" - MIDI: Received start message")
            if self.clock_target is not None:
                self.clock_target.start()

        elif message.type == 'stop':
            logger.info(" - MIDI: Received stop message")
            if self.clock_target is not None:
                self.clock_target.stop()

        elif message.type == 'songpos':
            logger.info(" - MIDI: Received songpos message")
            if message.pos == 0:
                if self.clock_target is not None:
                    self.clock_target.reset()
            else:
                logger.warning("MIDI song position message received, but MIDI input cannot seek to arbitrary position")

        elif message.type in ['note_on', 'note_off', 'control_change', 'pitchwheel', 'aftertouch', 'polytouch']:
            if message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                #------------------------------------------------------------------------
                # Note off event
                #------------------------------------------------------------------------
                if self.notes_down_dict[message.note] is not None:
                    note = self.notes_down_dict[message.note]
                    self.notes_down_dict[message.note] = None
                    self.notes_down.remove(note)
                    if self.on_note_off_handler:
                        self.on_note_off_handler(note)

            elif message.type == 'note_on':
                #------------------------------------------------------------------------
                # Note on event
                #------------------------------------------------------------------------
                if self.notes_down_dict[message.note] is None:
                    note = MidiNote(pitch=message.note,
                                    velocity=message.velocity,
                                    channel=message.channel)
                
                    self.notes_down.append(note)
                    self.notes_down_dict[message.note] = note

                    if self.on_note_on_handler:
                        self.on_note_on_handler(note)
            
            elif message.type == 'control_change':
                #------------------------------------------------------------------------
                # Control change event
                #------------------------------------------------------------------------
                # TODO: This passes a mido message. Should be an isobar structure.
                if self.on_control_change_handler:
                    self.on_control_change_handler(message)

            elif message.type == 'pitchwheel':
                #------------------------------------------------------------------------
                # Pitch bend event
                #------------------------------------------------------------------------
                if self.on_pitchbend_handler:
                    self.on_pitchbend_handler(message)
            
            elif message.type == 'aftertouch':
                #------------------------------------------------------------------------
                # Aftertouch event
                #------------------------------------------------------------------------
                for note in self.notes_down:
                    note.aftertouch = message.value
                if self.on_aftertouch_handler:
                    self.on_aftertouch_handler(message)

            elif message.type == 'polytouch':
                #------------------------------------------------------------------------
                # Polyphonic aftertouch event
                #------------------------------------------------------------------------
                note = self.notes_down_dict[message.note]
                note.aftertouch = message.value
                if self.on_polytouch_handler:
                    self.on_polytouch_handler(message)
            
            if self.callback:
                self.callback(message)
            else:
                self.queue.put(message)

    def stop(self):
        pass

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
        self.midi.close()
        del self.midi

    def set_note_on_handler(self, handler: Callable):
        """
        Set the function to call when a note on event is received.
        The function should take a single argument, which is the MidiNote object.

        Args:
            handler (Callable): The function to call.
        """
        self.on_note_on_handler = handler
    
    def set_note_off_handler(self, handler: Callable):
        """
        Set the function to call when a note off event is received.

        Args:
            handler (Callable): The function to call.
        """
        self.on_note_off_handler = handler
    
    def set_control_change_handler(self, handler: Callable):
        """
        Set the function to call when a control change event is received.

        Args:
            handler (Callable): The function to call.
        """
        self.on_control_change_handler = handler

    def set_polytouch_handler(self, handler: Callable):
        """
        Set the function to call when a polyphonic aftertouch event is received.

        Args:
            handler (Callable): The function to call.
        """
        self.on_polytouch_handler = handler

    def set_aftertouch_handler(self, handler: Callable):
        """
        Set the function to call when an aftertouch event is received.
        Args:
            handler (Callable): The function to call.
        """
        self.on_aftertouch_handler = handler