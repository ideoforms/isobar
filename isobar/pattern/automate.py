from isobar.pattern import *

import math

class PAutomate(Pattern):
    pass

class PASine(PAutomate):
    def __init__(self, length = 1, amp = 0.5):
        self.length = length
        self.amp = amp
        self.pos = 0.0

    def tick(self, tick_length):
        pos_norm = self.pos / self.length
        rv = math.sin(2.0 * math.pi * pos_norm) * self.amp
        #------------------------------------------------------------------------
        # normalize to [0, 1]
        #------------------------------------------------------------------------
        rv = 0.5 * rv + 0.5

        self.pos += tick_length
        if self.pos > self.length:
            self.pos -= self.length

        return rv
