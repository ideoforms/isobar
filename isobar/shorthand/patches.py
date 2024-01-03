from signalflow import *
import os
import numpy as np

class SegmentPlayerPatch (Patch):
    def __init__(self, buf, onsets, volume=0.5, hpf=10, lpf=20000, delay=0.0, feedback=0.0, pan=0.0, index=0, rate=1.0):
        super().__init__()
        index = self.add_input("index", index)
        rate = self.add_input("rate", rate)
        pan = self.add_input("pan", pan)
        volume = self.add_input("volume", volume)
        hpf = self.add_input("hpf", hpf)
        lpf = self.add_input("lpf", lpf)
        delay = self.add_input("delay", delay)
        feedback = self.add_input("feedback", feedback)
        player = SegmentPlayer(buf, onsets, rate=rate, index=index)
        stereo = StereoBalance(player * volume, pan)
        filtered = SVFilter(stereo, "low_pass", lpf)
        filtered = SVFilter(filtered, "high_pass", hpf)
        delayed = CombDelay(filtered, 0.25, feedback=feedback)
        output = filtered + delayed * delay
        self.set_trigger_node(player)
        self.set_output(output)

def segmenter(filename):
    buf = Buffer(filename)
    prefix, _ = os.path.splitext(filename)
    metadata_file = "%s.csv" % prefix
    onsets = list(np.loadtxt(metadata_file))
    patch = SegmentPlayerPatch(buf, onsets)
    patch.play()
    return patch
