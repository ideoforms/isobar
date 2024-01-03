from signalflow import *
from .setup import track, timeline

def start_sync_test():
    """
    Play metronome audio from SignalFlow and MIDI outputs, to help with
    establishing audio sync between the two. Latency of the SignalFlow output
    can be adjusted with the `added_latency_seconds` to the
    SignalFlowOutputDevice (see code above).
    """
    class ClickPatch (Patch):
        def __init__(self):
            super().__init__()
            impulse = StereoPanner(Impulse(0))
            self.set_output(impulse)
            self.set_auto_free_node(impulse)

    track(name='t0',
          dur=1.0,
          note="60")

    track(name='t1',
          patch=ClickPatch,
          duration=1)

def stop_sync_test():
    timeline.clear()
