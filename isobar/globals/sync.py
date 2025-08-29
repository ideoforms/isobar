from rpyc.utils.server import ThreadedServer
from isobar import Key
import threading
import logging
import rpyc
from .globals import Globals

logger = logging.getLogger(__name__)

# Auto-sensing client-server architecture:
#  - if a server already exists on localhost, connect to it
#  - if not, start one and connect

GLOBALS_SYNC_PORT = 18001

class GlobalsSyncService(rpyc.Service):
    def __init__(self):
        super().__init__()
        self.callbacks = []

    def set(self, key, value):
        valid_callbacks = []
        for callback in self.callbacks:
            try:
                callback(key, value)
                valid_callbacks.append(callback)
            except EOFError:
                print("Lost client, removing callback")
        self.callbacks = valid_callbacks

    def register_callback(self, fn):
        self.callbacks.append(fn)
        # When a client first connects, dump the full dictionary
        for key, value in Globals.dict.items():
            fn(key, value)

class GlobalsSyncServer:
    def __init__(self):
        self.service = GlobalsSyncService()
        self.server = ThreadedServer(self.service,
                                     hostname="127.0.0.1",
                                     port=GLOBALS_SYNC_PORT,
                                     protocol_config={'allow_public_attrs': True})
        self.thread = threading.Thread(target=self.server.start)
        self.thread.daemon = True 
        self.thread.start()

class GlobalsSyncClient:
    def __init__(self):
        conn = rpyc.connect("127.0.0.1", GLOBALS_SYNC_PORT)
        self.thread = rpyc.BgServingThread(conn)
        self.client = conn.root

        def on_globals_changed_local(key, value):
            value = repr(value)
            self.client.set(key, value)

        Globals.add_on_change_callback(on_globals_changed_local)

        def on_globals_changed_remote(key, value):
            if isinstance(value, str):
                try:
                    value = eval(value)
                except Exception as e:
                    pass

            # don't call Globals.set() to avoid circular callback triggers
            if key not in Globals.dict or Globals.dict[key] != value:
                Globals.dict[key] = value
            logging.debug("New globals values: %s" % Globals.dict)
    
        self.client.register_callback(on_globals_changed_remote)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")
    Globals.enable_interprocess_sync()

    while True:
        value = input()
        try:
            value = eval(value)
        except:
            pass
        Globals.set("value", value)