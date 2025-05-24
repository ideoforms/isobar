from ..output import OutputDevice

class ProxyOutputDevice (OutputDevice):
    def __init__(self, target_hostname):
        super().__init__()
        self.target_hostname = target_hostname

    def send(self, event):
        serialised = event.to_json()