import sys
import copy
import random

from .core import Pattern
from ..util import wnchoice

class PWhite(Pattern):
    """ PWhite: White noise between <min> and <max>.
       If values are given as floats, output values are also floats < max.
       If values are ints, output values are ints <= max (as random.randint)

        >>> PWhite(0, 10).nextn(16)
        [8, 10, 8, 1, 7, 3, 1, 9, 9, 3, 2, 10, 7, 5, 10, 4]

        >>> PWhite(0.0, 10.0).nextn(16)
        [3.6747936220022082, 0.61313530428271923, 9.1515368696591555, ... 6.2963694390145974 ]
       """

    def __init__(self, min, max=None):
        self.min = min
        self.max = max

        # also support a 1-argument case: PWhite(max)
        if self.max is None:
            self.max = min
            self.min = -self.max

    def __next__(self):
        min = Pattern.value(self.min)
        max = Pattern.value(self.max)

        if type(min) == float:
            return random.uniform(min, max)
        else:
            return random.randint(min, max)


class PBrown(Pattern):
    """ PBrown: Brownian noise.
                Output begins at <initial_value>, and steps up/down
                by uniform random values from [-<step>, <step>]
                inclusive.

                If step is a float, the output is a float pattern.
                If step is an int, the output is an int pattern,
                with min <= values <= max.
        """

    def __init__(self, initial_value=0, step=0.1, min=-sys.maxsize, max=sys.maxsize):
        """
        Args:
            initial_value (float or int): Initial value
            step (float or int): Maximum value to increase or decrease by each step
            min (float or int): Minimum permitted value
            min (float or int): Maximum permitted value
        """
        self.initial_value = initial_value
        self.value = initial_value
        self.step = step
        self.min = min
        self.max = max

    def reset(self):
        super().reset()
        self.value = self.initial_value

    def __next__(self):
        vstep = Pattern.value(self.step)
        vmin = Pattern.value(self.min)
        vmax = Pattern.value(self.max)

        rv = self.value
        if type(vstep) == float:
            self.value += random.uniform(-vstep, vstep)
        else:
            # select new offset
            steps = list(range(-vstep, vstep + 1))
            self.value += random.choice(steps)
        self.value = min(max(self.value, vmin), vmax)

        return rv


class PRandomWalk(Pattern):
    """ PWalk: Random walk around list.
               Jumps between <min> and <max> steps inclusive.

        >>> PRandomWalk([ 0, 2, 5, 8, 11 ], min=1, max=2).nextn(16)
        [8, 11, 0, 8, 0, 11, 2, 11, 2, 0, 5, 8, 11, 8, 5, 8]
        """

    def __init__(self, values=[], min=1, max=1, wrap=True):
        """

        Args:
            values (list): Array of values to walk around
            min (int): Minimum number of steps to move
            max (int): Maximum number of steps to move
            wrap (bool): Whether to wrap around the start/end of the array
        """
        self.values = values
        self.min = min
        self.max = max
        self.wrap = wrap
        self.reset()

    def reset(self):
        super().reset()
        self.pos = 0

    def __next__(self):
        vvalues = Pattern.value(self.values)
        vmin = Pattern.value(self.min)
        vmax = Pattern.value(self.max)

        move = random.randint(vmin, vmax)
        move = 0 - move if random.uniform(0, 1) < 0.5 else move
        self.pos += move

        if self.wrap:
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

    def __init__(self, values=[]):
        self.values = values

    def __next__(self):
        vvalues = Pattern.value(self.values)
        return random.choice(vvalues)

class PWeightedChoice(Pattern):
    """ PWeightedChoice: Random selection from <values>, weighted by <weights>.
                  <weights> and <values> must be the same length, but not
                  necessarily normalised.

        >>> p = PWeightedChoice([ 1, 11, 111 ], [ 8, 2, 1 ])
        >>> p.nextn(16)
        [111, 1, 1, 111, 1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1]
        """

    def __init__(self, values=[], weights=[]):
        self.values = values
        self.weights = weights

    def __next__(self):
        vvalues = Pattern.value(self.values)
        vweights = Pattern.value(self.weights)
        return wnchoice(vvalues, vweights)


class PShuffle(Pattern):
    """ PShuffle: Shuffled list.

        >>> p = PShuffle([ 1, 2, 3 ])
        >>> p.nextn(16)
        [1, 3, 2, 3, 2, 1, 2, 3, 1, 2, 3, 1, 1, 2, 3, 1]
        """

    def __init__(self, values=[], repeats=sys.maxsize):
        """

        Args:
            values (list): List of values
            repeats (int): Number of times to re-shuffle and iterate
        """
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
        values = Pattern.value(self.values)
        repeats = Pattern.value(self.repeats)

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

    def __init__(self, pattern, every=4):
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

class PSkip(Pattern):
    """ PSkip: Skip events with some probability, 1 - <play>.
               Set <regularise> to True to skip events regularly.
        """

    def __init__(self, pattern, play, regularise=False):
        self.pattern = pattern
        self.play = play
        self.regularise = regularise
        self.pos = 0.0

    def __next__(self):
        play = Pattern.value(self.play)
        value = next(self.pattern)

        if self.regularise:
            self.pos += play
            if self.pos >= 1:
                self.pos -= 1
                return value
        else:
            if random.uniform(0, 1) < self.play:
                return value

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

    def __init__(self, initial=0, p_on=0.5, p_off=0.5):
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
    """ PSwitchOne: Capture <length> input values; repeat, switching two adjacent values.
        """

    def __init__(self, pattern, length=4):
        self.pattern = pattern
        self.length = length

        self.reset()

    def reset(self):
        super().reset()
        self.values = []
        self.pos = 0

    def __next__(self):
        length = self.value(self.length)

        if len(self.values) < length:
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
