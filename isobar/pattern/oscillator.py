""" oscillator.py: Regular waveforms as pattern generators. """

from __future__ import annotations
from .core import Pattern

class PTri(Pattern):
    """ PTri: Generates a triangle waveform of period `length`.

        >>> p = PTri(10)
        >>> p.nextn(10)
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]
        """

    def __init__(self, length: int = 10, min: float = 0.0, max: float = 1.0):
        self.length = length
        self.min = min
        self.max = max
        self.reset()

    def __repr__(self):
        return ("PTri(%s, %s, %s)" % (self.length, self.min, self.max))

    def reset(self):
        self.phase = 0.0

    def __next__(self):
        length = Pattern.value(self.length)
        min = Pattern.value(self.min)
        max = Pattern.value(self.max)

        norm_phase = float(self.phase) / length
        if norm_phase < 0.5:
            rv = norm_phase * 2.0
        else:
            rv = 1.0 - (norm_phase - 0.5) * 2.0
        rv = min + (max - min) * rv

        self.phase += 1
        if self.phase > length:
            self.phase -= length

        return rv

class PSaw(Pattern):
    """ PSaw: Generates a sawtooth waveform.

        >>> p = PTri(10)
        >>> p.nextn(10)
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]
        """

    def __init__(self, length=10, min=0.0, max=1.0):
        self.length = length
        self.min = min
        self.max = max
        self.reset()

    def reset(self):
        self.phase = 0.0

    def __next__(self):
        length = Pattern.value(self.length)
        min = Pattern.value(self.min)
        max = Pattern.value(self.max)

        norm_phase = float(self.phase) / length
        rv = norm_phase
        rv = min + (max - min) * rv

        self.phase += 1
        if self.phase > length:
            self.phase -= length

        return rv
