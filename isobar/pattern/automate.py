from isobar.pattern import *

import math

class PAutomate(Pattern):
    pass

class PASine(PAutomate):
    def __init__(self, length = 1, amp = 0.5):
        self.length = length
        self.amp = amp
        self.pos = 0.0

    def play(self, device):
        self.pos += 1/64.0
        if self.pos > self.length:
            self.pos = 0

        # normalize to [0, 1]
        pos_norm = self.pos / self.length
        warp = math.sin(2.0 * math.pi * pos_norm) * self.amp
        # print "warp, %f" % warp
        print "warp is %d" % int(warp * 64 + 64)
        device.control(0, int(warp * 64 + 64))
