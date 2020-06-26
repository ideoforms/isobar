from ..output import OutputDevice

try:
    import pythonosc
    from pythonosc.udp_client import SimpleUDPClient
    from pythonosc.osc_message import OSCMessage
except:
    pass

class OSCOut (OutputDevice):
    """
    OSCOut: Wraps MIDI messages in OSC.
    /note [ note, velocity, channel ]
    /control [ control, value, channel ]
    """

    def __init__(self, host, port):
        """
        Args:
            host: Hostname to send OSC messages to
            port: Port number to send OSC messages to
        """
        try:
            self.osc = SimpleUDPClient(host, port)

        except NameError:
            raise Exception("python-osc must be installed")

    def note_on(self, note=60, velocity=64, channel=0):
        self.osc.send_message("/note", velocity, channel)

    def note_off(self, note=60, channel=0):
        self.osc.send_message("/note", 0, channel)

    def control(self, control, value, channel=0):
        self.osc.send_message("/control", value, channel)

    def send(self, address, params=None):
        self.osc.send_message(address, params)
