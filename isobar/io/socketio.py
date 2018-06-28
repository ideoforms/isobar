import random
import time
import socketIO_client

from isobar.note import *

class SocketIOOut:
    """ SocketIOOut: Support for sending note on/off events via websockets.
    Two types of event are sent at the moment:

    note [ index, velocity, channel ] : The MIDI note number depressed.
                                        For note-off, velocity is zero.
    control [ index, value, channel ] : A MIDI control value 
    """

    def __init__(self, host = "localhost", port = 9000):
        self.socket = socketIO_client.SocketIO(host, port)

    def tick(self, tick_length):
        pass

    def event(self, event):
        # import pprint
        # pprint.pprint(event)
        self.socket.emit("event", event)

    def note_on(self, note = 60, velocity = 64, channel = 0):
        self.socket.emit("note", note, velocity, channel)

    def note_off(self, note = 60, channel = 0):
        self.socket.emit("note", note, 0, channel)

    def all_notes_off(self, channel = 0):
        for n in range(128):
            self.note_off(n, channel)

    def control(self, control, value, channel = 0):
        self.socket.emit("control", control, value, channel)

    def __destroy__(self):
        self.socket.close()

