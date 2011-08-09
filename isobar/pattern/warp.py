from isobar.pattern import *

import math

class PWarp(Pattern):
    pass

class PWRamp(PWarp):
    def __init__(self, length = 1, slope = -0.5):
        self.length = length
        self.slope = slope
        self.vslope = self.value(slope)
        self.pos = 0.0

    def next(self):
        self.pos += 1/64.0
        if self.pos > self.length:
            self.pos = 0
            self.vslope = self.value(self.slope)
            # print "new slope %s" % self.vslope

        # normalize to [-1, 1]
        pos_norm = 2.0 * self.pos / self.length - 1.0
        warp = (pos_norm * self.vslope)
        # print "warp, %f" % warp
        return warp

class PWSine(PWarp):
    def __init__(self, length = 1, amp = 0.5):
        self.length = length
        self.amp = amp
        self.pos = 0.0

    def next(self):
        self.pos += 1/64.0
        if self.pos > self.length:
            self.pos = 0

        # normalize to [0, 1]
        pos_norm = self.pos / self.length
        warp = math.sin(2.0 * math.pi * pos_norm)
        warp = warp * self.amp
        # print "warp, %f" % warp
        return warp
