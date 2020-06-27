from ..output import OutputDevice

class SocketIOOutputDevice (OutputDevice):
    """ SocketIOOutputDevice: Support for sending note on/off events via websockets.
    Two types of event are sent at the moment:

    note [ index, velocity, channel ] : The MIDI note number depressed.
                                        For note-off, velocity is zero.
    control [ index, value, channel ] : A MIDI control value
    """

    def __init__(self, host="localhost", port=9000):
        import socketIO_client
        self.socket = socketIO_client.SocketIO(host, port)

    def event(self, event):
        self.socket.emit("event", event)

    def note_on(self, note=60, velocity=64, channel=0):
        self.socket.emit("note", note, velocity, channel)

    def note_off(self, note=60, channel=0):
        self.socket.emit("note", note, 0, channel)

    def control(self, control, value, channel=0):
        self.socket.emit("control", control, value, channel)

    def __destroy__(self):
        self.socket.close()
