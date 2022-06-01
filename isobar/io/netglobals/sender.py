from pythonosc.udp_client import SimpleUDPClient
import time
import pickle
from isobar.pattern.static import Globals

class NetworkGlobalsSender:
    """
    Simple interface to send globals over a network.
    Currently assumes virtually no network latency or jitter, so is only suitable
    for Ethernet connections!

    TODO: Implement round-trip latency estimation and jitter smoothing.
    """
    def __init__(self, destination_host, destination_port=8193):
        self.destination_host = destination_host
        self.destination_port = destination_port
        self.osc_client = SimpleUDPClient(self.destination_host, self.destination_port)
        Globals.on_change_callback = self.on_globals_change

    def on_globals_change(self, key, value):
        if isinstance(value, (float, int, str, bool)):
            self.osc_client.send_message("/globals/set", [key, value])
        else:
            self.osc_client.send_message("/globals/set", [key, pickle.dumps(value)])

if __name__ == "__main__":
    import random
    sender = NetworkGlobalsSender("127.0.0.1")
    while True:
        value = random.uniform(0, 1)
        print("Sending: %.3f" % value)
        Globals.set("test", value)
        time.sleep(1.0)
