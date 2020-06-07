from ..output import OutputDevice

class OSCOut (OutputDevice):
    """ OSCOut: Wraps MIDI messages in OSC.
    /note [ note, velocity, channel ]
    /control [ control, value, channel ] """

    def __init__(self, host="localhost", port=7000):
        from pythonosc.udp_client import SimpleUDPClient
        self.osc = SimpleUDPClient(host, port)

    def tick(self, tick_length):
        pass

    def note_on(self, note=60, velocity=64, channel=0):
        msg = OSCMessage("/note")
        self.osc.send_message("/note", velocity, channel)

    def note_off(self, note=60, channel=0):
        self.osc.send_message("/note", 0, channel)

    def control(self, control, value, channel=0):
        self.osc.send_message("/control", value, channel)

    def __destroy__(self):
        pass

    def send(self, address, params=None):
        self.osc.send_message(address, *params)
