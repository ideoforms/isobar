""" oscillator.py: Regular waveforms as pattern generators. """

import sys
import copy
import itertools

from isobar.pattern.core import *

class PTri(Pattern):
    """ PTri: Generates a triangle waveform of period <length>.

        >>> p = PTri(10)
        >>> p.nextn(10)
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]
        """

    def __init__(self, length = 10):
        self.length = length
        self.reset()

    def reset(self):
        self.phase = 0.0

    def __next__(self):
        length = Pattern.value(self.length)

        norm_phase = float(self.phase) / length
        if norm_phase < 0.5:
            rv = norm_phase * 2.0
        else:
            rv = 1.0 - (norm_phase - 0.5) * 2.0

        self.phase += 1
        if self.phase > length:
            self.phase -= length

        return rv

