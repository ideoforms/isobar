import sys
import random
import itertools

from isobar.pattern.core import *
from isobar.util import *

class PWhite(Pattern):
    """ PWhite: White noise between <min> and <max>.
       If values are given as floats, output values are also floats < max.
       If values are ints, output values are ints <= max (as random.randint)

        >>> PWhite(0, 10).nextn(16)
        [8, 10, 8, 1, 7, 3, 1, 9, 9, 3, 2, 10, 7, 5, 10, 4]

        >>> PWhite(0.0, 10.0).nextn(16)
        [3.6747936220022082, 0.61313530428271923, 9.1515368696591555, ... 6.2963694390145974 ]
       """
    def __init__(self, min, max = None):
        self.min = min
        self.max = max

        # also support a 1-argument case: PWhite(max)
        if self.max is None:
            self.max = min
            self.min = -self.max

    def __next__(self):
        min = self.value(self.min)
        max = self.value(self.max)

        if type(min) == float:
            return random.uniform(min, max)
        else:
            return random.randint(min, max)

class PBrown(Pattern):
    """ PBrown: Brownian noise, beginning at <value>, step +/-<step>.
                Set <repeats> to False to prevent consecutive repeats.
        """
    def __init__(self, value = 0, step = 0.1, min = -sys.maxsize, max = sys.maxsize, repeats = True, length = sys.maxsize):
        self.init = value
        self.value = value
        self.step = step
        self.min = min
        self.max = max
        self.length = length
        self.repeats = repeats
        self.pos = 0

    def reset(self):
        self.value = self.init
        self.pos = 0

        Pattern.reset(self)

    def __next__(self):
        # pull out modulatable values
        vstep    = Pattern.value(self.step)
        vmin     = Pattern.value(self.min)
        vmax     = Pattern.value(self.max)
        vrepeats = Pattern.value(self.repeats)

        if self.pos >= self.length:
            raise StopIteration
        rv = self.value
        self.pos += 1
        if type(vstep) == float:
            self.value += random.uniform(-vstep, vstep)
        else:
            # select new offset without repeats
            steps = list(range(-vstep, vstep + 1))
            if not vrepeats:
                steps.remove(0)
            self.value += random.choice(steps)
        self.value = min(max(self.value, vmin), vmax)

        return rv


class PWalk(Pattern):
    """ PWalk: Random walk around list.
               Jumps between <min> and <max> steps inclusive.

        >>> PWalk([ 0, 2, 5, 8, 11 ], min = 1, max = 2).nextn(16)
        [8, 11, 0, 8, 0, 11, 2, 11, 2, 0, 5, 8, 11, 8, 5, 8]
        """
    def __init__(self, values = [], min = 1, max = 1):
        self.values = values
        self.min = min
        self.max = max
        self.pos = 0

    def __next__(self):
        vvalues = Pattern.value(self.values)
        vmin    = Pattern.value(self.min)
        vmax    = Pattern.value(self.max)

        move = random.randint(vmin, vmax)
        move = 0 - move if random.uniform(0, 1) < 0.5 else move
        self.pos += move

        while self.pos < 0:
            self.pos += len(vvalues)
        while self.pos >= len(vvalues):
            self.pos -= len(vvalues)

        return vvalues[self.pos]


class PChoice(Pattern):
    """ PChoice: Random selection from <values>

        >>> p = PChoice([ 0, 1, 10, 11 ])
        >>> p.nextn(16)
        [11, 1, 0, 10, 1, 11, 1, 0, 11, 1, 11, 1, 1, 11, 11, 1]
        """
    def __init__(self, values = []):
        self.values = values

    def __next__(self):
        return self.values[random.randint(0, len(self.values) - 1)]

class PWChoice(Pattern):
    """ PWChoice: Random selection from <values>, weighted by <weights>.
                  <weights> and <values> must be the same length, but not
                  necessarily normalised.

        >>> p = PWChoice([ 1, 11, 111 ], [ 8, 2, 1 ])
        >>> p.nextn(16)
        [111, 1, 1, 111, 1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1]
        """
    def __init__(self, values = [], weights = []):
        self.values = values
        self.weights = weights

    def __next__(self):
        return wnchoice(self.values, self.weights)

class PShuffle(Pattern):
    """ PShuffle: Shuffled list.

        >>> p = PShuffle([ 1, 2, 3 ])
        >>> p.nextn(16)
        [1, 3, 2, 3, 2, 1, 2, 3, 1, 2, 3, 1, 1, 2, 3, 1]
        """
    def __init__(self, values = [], repeats = sys.maxsize):
        self.values = copy.copy(values)
        self.repeats = repeats

        self.pos = 0
        self.rcount = 1
        random.shuffle(self.values)

    def reset(self):
        self.pos = 0
        self.rcount = 0
        random.shuffle(self.values)

        Pattern.reset(self)

    def __next__(self):
        values = self.value(self.values)
        repeats = self.value(self.repeats)

        if self.pos >= len(values):
            if self.rcount >= repeats:
                raise StopIteration
            random.shuffle(self.values)
            self.rcount += 1
            self.pos = 0

        rv = values[self.pos]
        self.pos += 1
        return rv

class PShuffleEvery(Pattern):
    """ PShuffleEvery: Every <n> steps, take <n> values from <pattern> and reorder.

        >>> p = PShuffleEvery(PSeries(0, 1), 4)
        >>> p.nextn(16)
        """
    def __init__(self, pattern, every = 4):
        self.pattern = pattern
        self.every = every
        self.values = []
        self.pos = 0

    def begin(self):
        kevery = Pattern.value(self.every)
        self.values = self.pattern.nextn(kevery)
        random.shuffle(self.values)
        self.pos = 0

    def reset(self):
        # TODO: clarify the semantics of "reset" (which should trickle down to children)
        #       vs the method called each time a new set of values is needed -- should
        #       this be a flag to reset?
        self.begin()
        Pattern.reset(self)

    def __next__(self):
        if self.pos >= len(self.values):
            self.begin()

        rv = self.values[self.pos]
        self.pos += 1
        return rv

class PSelfIndex(Pattern):
    def __init__(self, count = 6):
        self.pos = 0
        self.values = list(range(count))
        random.shuffle(self.values)
        print("init values: %s" % self.values)

    def __next__(self):
        if self.pos >= len(self.values):
            # re-index values
            self.pos = 0
            self.reindex()

        rv = self.values[self.pos]
        self.pos += 1

        return rv

    def reindex(self):
        values_new = []
        for n in range(len(self.values)):
            values_new.append(self.values[self.values[n]])
        print("new ordering: %s" % values_new)
        self.values = values_new

class PSkip(Pattern):
    """ PSkip: Skip events with some probability, 1 - <play>.
               Set <random> to False to skip events regularly.
        """
    def __init__(self, pattern, play, random = True):
        self.pattern = pattern
        self.play = play
        self.random = random
        self.pos = 0.0

    def __next__(self):
        play = self.value(self.play)
        if self.random:
            if random.uniform(0, 1) < self.play:
                return next(self.pattern)
        else:
            self.pos += play
            if self.pos >= 1:
                self.pos -= 1
                return next(self.pattern)
        return None

class PFlipFlop(Pattern):
    """ PFlipFlop: flip a binary bit with some probability.
                   <initial> is initial value (0 or 1)
                   <p_on> is chance of switching from 0->1
                   <p_off> is chance of switching from 1->0

        >>> p = PFlipFlop(0, 0.9, 0.5)
        >>> p.nextn(16)
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        """
    def __init__(self, initial = 0, p_on = 0.5, p_off = 0.5):
        self.value = initial
        self.p_on = p_on
        self.p_off = p_off

    def __next__(self):
        self.value = Pattern.value(self.value)
        self.p_on = Pattern.value(self.p_on)
        self.p_off = Pattern.value(self.p_off)

        if self.value == 0:
            if random.uniform(0, 1) < self.p_on:
                self.value = 1
        else:
            if random.uniform(0, 1) < self.p_off:
                self.value = 0

        return self.value

class PSwitchOne(Pattern):
    """ PSwitchOne: Capture <length> input values; repeat, switching two adjacent values <n> times.
        """
    def __init__(self, pattern, length = 4, switches = 1):
        self.pattern = pattern
        self.length = length
        self.switches = switches

        self.reset()

    def reset(self):
        self.values = []
        self.pos = 0

        # recursively reset my pattern fields
        Pattern.reset(self)

    def __next__(self):
        length = self.value(self.length)
        switches = self.value(self.switches)

        if len(self.values) < self.length:
            value = next(self.pattern)
            self.values.append(value)
            self.pos += 1
            return value

        if self.pos >= len(self.values):
            index = random.randint(0, len(self.values)) - 1
            indexP = (index + 1) % len(self.values)
            self.values[index], self.values[indexP] = self.values[indexP], self.values[index]
            self.pos = 0

        rv = self.values[self.pos]
        self.pos += 1
        return rv

