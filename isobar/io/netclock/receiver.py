from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import time

from ...constants import DEFAULT_TICKS_PER_BEAT

class NetworkClockReceiver:
    """
    Naive interface to send clock signals over a network.
    Currently assumes virtually no network latency or jitter, so is only suitable
    for Ethernet connections!

    TODO: Implement round-trip latency estimation and jitter smoothing.
    """
    def __init__(self, clock_target=None, port=8192, ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
        self.clock_target = clock_target

        dispatcher = Dispatcher()
        dispatcher.map("/clock/tick", self.clock_handler)

        server = BlockingOSCUDPServer(("127.0.0.1", port), dispatcher)
        self.thread = threading.Thread(target=server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        self.ticks_per_beat = ticks_per_beat

    def run(self):
        while True:
            time.sleep(0.1)

    def clock_handler(self, address, *args):
        if self.clock_target:
            self.clock_target.tick()

if __name__ == "__main__":
    class DummyClockTarget:
        def tick(self):
            print("tick")
    receiver = NetworkClockReceiver(clock_target=DummyClockTarget())
    while True:
        time.sleep(0.1)