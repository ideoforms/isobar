class ProxyOutputDeviceReceiver:
    def __init__(self, output_device):
        self.output_device = output_device
    
    def run(self):
        timeline = Timeline()
        track = Track(timeline=timeline,
                      output_device=self.output_device)
        