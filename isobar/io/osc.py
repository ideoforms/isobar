import random
import time

from pythonosc.udp_client import SimpleUDPClient

from isobar.note import *

MIDIIN_DEFAULT = "IAC Driver A"
MIDIOUT_DEFAULT = "IAC Driver A"

class OSCOut:
    """ OSCOut: Wraps MIDI messages in OSC.
    /note [ note, velocity, channel ]
    /control [ control, value, channel ] """

    def __init__(self, host = "localhost", port = 7000):
        self.osc = SimpleUDPClient(host, port)

    def tick(self, tick_length):
        pass

    def note_on(self, note = 60, velocity = 64, channel = 0):
        msg = OSCMessage("/note")
        self.osc.send_message("/note", velocity, channel)

    def note_off(self, note = 60, channel = 0):
        self.osc.send_message("/note", 0, channel)

    def all_notes_off(self, channel = 0):
        for n in range(128):
            self.note_off(n, channel)

    def control(self, control, value, channel = 0):
        self.osc.send_message("/control", value, channel)

    def __destroy__(self):
        pass

    def send(self, address, params = None):
        self.osc.send_message(address, *params)
