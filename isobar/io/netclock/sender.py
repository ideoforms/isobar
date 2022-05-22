from pythonosc.udp_client import SimpleUDPClient
import time

class NetworkClockSender:
    """
    Naive interface to send clock signals over a network.
    Currently assumes virtually no network latency or jitter, so is only suitable
    for Ethernet connections!

    TODO: Implement round-trip latency estimation and jitter smoothing.
    """
    def __init__(self, destination_host, destination_port=8192):
        self.destination_host = destination_host
        self.destination_port = destination_port
        self.osc_client = SimpleUDPClient(self.destination_host, self.destination_port)

    def tick(self):
        self.osc_client.send_message("/clock/tick", [])

    def reset(self):
        self.osc_client.send_message("/clock/reset", [])

    def sync_beat(self):
        self.osc_client.send_message("/clock/sync/beat", [])

if __name__ == "__main__":
    sender = NetworkClockSender("127.0.0.1")
    sender.reset()
    while True:
        time.sleep(0.1)
        sender.tick()