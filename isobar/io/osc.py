import random
import time

from OSC import *

from isobar.note import *

MIDIIN_DEFAULT = "IAC Driver A"
MIDIOUT_DEFAULT = "IAC Driver A"

class OSCOut:
    """ OSCOut: Wraps MIDI messages in OSC.
    /note [ note, velocity, channel ]
    /control [ control, value, channel ] """

    def __init__(self, host = "localhost", port = 7000):
        self.osc = OSCClient()
        self.osc.connect((host, port))

    def tick(self, tick_length):
        pass

    def note_on(self, note = 60, velocity = 64, channel = 0):
        msg = OSCMessage("/note")
        msg.extend([ note, velocity, channel ])
        self.osc.send(msg)

    def note_off(self, note = 60, channel = 0):
        msg = OSCMessage("/note")
        msg.extend([ note, 0, channel ])
        self.osc.send(msg)

    def all_notes_off(self, channel = 0):
        for n in range(128):
            self.note_off(n, channel)

    def control(self, control, value, channel = 0):
        msg = OSCMessage("/control")
        msg.extend([ control, value, channel ])
        self.osc.send(msg)

    def __destroy__(self):
        self.osc.close()

    def send(self, address, params = None):
        msg = OSCMessage(address)
        msg.extend(params)
        print "osc: %s (%s)" % (address, params)
        self.osc.send(msg)

