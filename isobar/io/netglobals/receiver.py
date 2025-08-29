from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import pickle
import time

from isobar.pattern.static import Globals
from isobar.constants import DEFAULT_TICKS_PER_BEAT

class NetworkGlobalsReceiver:
    """
    Simple interface to receive Globals over a network.

    TODO: Integrate with NetworkClockReceiver
    """

    def __init__(self, port=8193):
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/globals/set", self.on_globals_set)
        self.port = port
        self.server = None
        self.running = False

    def start(self):
        self.server = BlockingOSCUDPServer(("0.0.0.0", self.port), self.dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.running = True

    def stop(self):
        self.server.shutdown()
        self.running = False

    def on_globals_set(self, address, *args):
        key = args[0]
        value = args[1]
        try:
            Globals.set(key, pickle.loads(value))
        except:
            Globals.set(key, value)

if __name__ == "__main__":
    receiver = NetworkGlobalsReceiver()
    receiver.start()
    Globals.set("test", 0.0)
    while True:
        time.sleep(1.0)
        print(Globals.get("test"))
