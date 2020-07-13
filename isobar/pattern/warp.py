from .core import Pattern

import math

class PWarp(Pattern):
    pass

class PWInterpolate(PWarp):
    """ PWInterpolate: Requests a new target warp value from `pattern` every `length` beats
        and applies linear interpolation to ramp between values.

        To select a new target warp value every 8 beats, between [-0.5, 0.5]:

        >>> p = PWInterpolate(PWhite(-0.5, 0.5), 8)
        """

    def __init__(self, pattern, length=1):
        self.length = length
        self.pattern = pattern
        self.pos = self.length
        self.value = 0.0
        self.dv = 0.0

    def __next__(self):
        rv = self.value

        #------------------------------------------------------------------------
        # keep ticking until we have reached our period (length, in beats)
        # TODO: querying self.timeline is very inefficient, find a better way
        #------------------------------------------------------------------------
        self.pos += self.timeline.tick_duration
        if self.pos >= self.length:
            self.pos = 0
            self.target = next(self.pattern)

            #------------------------------------------------------------------------
            # in case our length parameter is also a pattern: obtain a scalar value.
            # dv is used for linear interpolation until the next target reached.
            #------------------------------------------------------------------------
            length = Pattern.value(self.length)
            self.dv = (self.target - self.value) / (self.timeline.ticks_per_beat * length)

        self.value = self.value + self.dv

        return rv

class PWSine(PWarp):
    """ PWSine: Sinosoidal warp, period `length` beats, amplitude +/-<amp>.

        >>> p = PWAmp(8, 0.5)
        """

    def __init__(self, length=1, amp=0.5):
        self.length = length
        self.amp = amp
        self.pos = 0.0

    def __next__(self):
        self.pos += self.timeline.tick_duration
        if self.pos > self.length:
            self.pos -= self.length

        # normalize to [0, 1]
        pos_norm = self.pos / self.length
        warp = math.sin(2.0 * math.pi * pos_norm)
        warp = warp * self.amp

        return warp

class PWRallantando(PWarp):
    """ PWRallantando: Exponential deceleration to <amp> times the current tempo over `length` beats.

        >>> p = PWRallantando(8, 0.5)
        """

    def __init__(self, length=1, amp=0.5):
        self.length = length
        self.amp = amp
        self.pos = 0.0
        self.value = 1.0
        self.length_cur = -1.0
        self.dv = None

    def __next__(self):
        rv = self.value

        #------------------------------------------------------------------------
        # Need to round to avoid Python rounding errors
        # (eg 0.99999 < 1 when multiplying 1/24.0 by 24)
        #------------------------------------------------------------------------
        if round(self.pos, 8) >= round(self.length_cur, 8):
            self.value = 1.0
            rv = 1.0
            self.pos = 0
            self.length_cur = Pattern.value(self.length)
            amp_cur = Pattern.value(self.amp)
            rate_start = 1.0
            rate_end = 1.0 + amp_cur
            steps = self.timeline.ticks_per_beat * self.length_cur
            self.dv = math.exp(math.log(rate_end / rate_start) / steps)

        self.pos += self.timeline.tick_duration
        self.value = self.value * self.dv

        rv = math.log(rv, 2)
        return rv
