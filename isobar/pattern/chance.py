import sys
import copy
import random

from .core import Pattern
from ..util import wnchoice

class PStochasticPattern(Pattern):
    """
    PStochasticPattern is the superclass of all chance-based patterns.
    It contains its own random number generator and state, so that it can be
    seeded independently of other RNG processes in the application.

    When it is created, a random seed is generated and stored.
    When reset() is called, the pattern's RNG is re-seeded with this same seed,
    allow it to rewind to the beginning of its random pattern.
    """
    def __init__(self):
        self.rng = random.Random()
        self._seed = self.rng.randint(0, sys.maxsize)
        self.rng.seed(self._seed)

    def reset(self):
        super().reset()
        self.rng.seed(self._seed)

    def seed(self, seed=None):
        """
        Seed the pattern's random number generator with a new seed,
        initialising a new pseudo-random sequence.

        Args:
            seed: A hashable value, or None. See pydoc random.
        """
        if seed is None:
            seed = random.randint(0, sys.maxsize)
        self._seed = seed
        self.rng.seed(self._seed)

class PWhite(PStochasticPattern):
    """ PWhite: White noise between `min` and `max`.
       If values are given as floats, output values are also floats < max.
       If values are ints, output values are ints <= max (as random.randint)

        >>> PWhite(0, 10).nextn(16)
        [8, 10, 8, 1, 7, 3, 1, 9, 9, 3, 2, 10, 7, 5, 10, 4]

        >>> PWhite(0.0, 10.0).nextn(16)
        [3.6747936220022082, 0.61313530428271923, 9.1515368696591555, ... 6.2963694390145974 ]
       """

    def __init__(self, min=0.0, max=1.0):
        super().__init__()

        self.min = min
        self.max = max

    def __next__(self):
        min = Pattern.value(self.min)
        max = Pattern.value(self.max)

        if type(min) == float:
            return self.rng.uniform(min, max)
        else:
            #--------------------------------------------------------------------------------
            # rng.randint does not spread values across the range proportionately with
            # varying values of [min, max]. Use rng.uniform() and do our own scaling to ensure
            # that the output is controllable.
            #--------------------------------------------------------------------------------
            rv = int(self.rng.uniform(min, max))
            return rv

class PBrown(PStochasticPattern):
    """ PBrown: Brownian noise.
                Output begins at `initial_value`, and steps up/down
                by uniform random values from [-`step`, `step`]
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
        super().__init__()
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
            self.value += self.rng.uniform(-vstep, vstep)
        else:
            # select new offset
            steps = list(range(-vstep, vstep + 1))
            self.value += self.rng.choice(steps)
        self.value = min(max(self.value, vmin), vmax)

        return rv


class PCoin(PStochasticPattern):
    """ PCoin: Coin toss, returning either 0 or 1 given some `probability`.
               `probability` is the chance of returning 1, and must be between [0, 1].

               This is a convenience pattern which could also be written
                as `PWhite(0, 1) < probability`

        >>> PCoin(0.75).nextn(16)
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1]
       """

    def __init__(self, probability=0.5):
        super().__init__()
        self.probability = probability

    def __next__(self):
        probability = Pattern.value(self.probability)

        if self.rng.uniform(0, 1) < probability:
            return 1
        else:
            return 0


class PRandomWalk(PStochasticPattern):
    """ PWalk: Random walk around list.
               Jumps between `min` and `max` steps inclusive.

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
        super().__init__()
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

        move = self.rng.randint(vmin, vmax)
        move = 0 - move if self.rng.uniform(0, 1) < 0.5 else move
        self.pos += move

        if self.wrap:
            while self.pos < 0:
                self.pos += len(vvalues)
            while self.pos >= len(vvalues):
                self.pos -= len(vvalues)

        return vvalues[self.pos]

class PChoice(PStochasticPattern):
    """ PChoice: Pick a random element from `values`, weighted by optional `weights`.
                 `weights` and `values` must be the same length.
                 weights do not need to be normalised.

        >>> p = PChoice([ 0, 1, 10, 11 ])
        >>> p.nextn(16)
        [11, 1, 0, 10, 1, 11, 1, 0, 11, 1, 11, 1, 1, 11, 11, 1]

        >>> p = PChoice([ 1, 11, 111 ], [ 8, 2, 1 ])
        >>> p.nextn(16)
        [111, 1, 1, 111, 1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1]
        """

    def __init__(self, values, weights=None):
        """
        Args:
            values: A list of values
            weights: An optional list of weights, of the same length as values
        """
        super().__init__()
        self.values = values
        self.weights = weights

    def __next__(self):
        vvalues = Pattern.value(self.values)
        vweights = Pattern.value(self.weights)
        if vweights is not None:
            return wnchoice(vvalues, vweights, rng=self.rng)
        else:
            return self.rng.choice(vvalues)


class PSample(PStochasticPattern):
    """ PSample: Pick multiple random elements from `values`, weighted by optional `weights`,
                 without replacement. Each return value is a list.

                 `weights` and `values` must be the same length.
                 weights do not need to be normalised.

        >>> p = PSample([1, 2, 3], count=2, weights=[1, 2, 3])
        >>> p.nextn(16)
        [[3, 2], [2, 3], [3, 2], [3, 1], [2, 3], [3, 2], [2, 3], [3, 1], [3, 2], [3, 2], [2, 3],
         [3, 2], [2, 1], [2, 3], [3, 2], [2, 3]]
        """

    def __init__(self, values, count, weights=None):
        """
        Args:
            values: A list of values
            weights: An optional list of weights, of the same length as values
        """
        super().__init__()
        self.values = values
        self.count = count
        self.weights = weights

    def __next__(self):
        vvalues = copy.copy(Pattern.value(self.values))
        vcount = copy.copy(Pattern.value(self.count))
        vweights = copy.copy(Pattern.value(self.weights))

        if vcount > len(vvalues):
            raise ValueError("Count cannot be larger than the number of available values")

        rv = []
        for n in range(vcount):
            if vweights:
                index = wnchoice(list(range(len(vvalues))), vweights, rng=self.rng)
                vweights.pop(index)
            else:
                index = self.rng.randrange(0, len(vvalues))

            rv.append(vvalues.pop(index))

        return rv

class PShuffle(PStochasticPattern):
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
        super().__init__()
        self.values_orig = copy.copy(values)
        self.repeats = repeats

        self.pos = 0
        self.rcount = 1
        self.values = copy.copy(self.values_orig)

    def reset(self):
        super().reset()
        self.pos = 0
        self.rcount = 0
        self.values = copy.copy(self.values_orig)

    def __next__(self):
        values = Pattern.value(self.values)
        repeats = Pattern.value(self.repeats)

        if self.pos == 0:
            self.rng.shuffle(self.values)

        if self.pos >= len(values):
            self.rcount += 1
            if self.rcount >= repeats:
                raise StopIteration
            self.pos = 0

        rv = values[self.pos]
        self.pos += 1
        return rv


class PShuffleInput(PStochasticPattern):
    """ PShuffleInput: Every `n` steps, take `n` values from `pattern` and reorder.

        >>> p = PShuffleInput(PSeries(0, 1), 4)
        >>> p.nextn(16)
        """

    def __init__(self, pattern, every=4):
        super().__init__()
        self.pattern = pattern
        self.every = every
        self.values = []
        self.pos = 0

    def __next__(self):
        if self.pos >= len(self.values):
            self.pos = 0

        if self.pos == 0:
            kevery = Pattern.value(self.every)
            self.values = self.pattern.nextn(kevery)
            self.rng.shuffle(self.values)

        rv = self.values[self.pos]
        self.pos += 1
        return rv

class PSkip(PStochasticPattern):
    """ PSkip: Skip events with some probability, 1 - <play>.
               Set <regularise> to True to skip events regularly.
        """

    def __init__(self, pattern, play, regularise=False):
        super().__init__()
        self.pattern = pattern
        self.play = play
        self.regularise = regularise
        self.pos = 0.0

    def __next__(self):
        value = Pattern.value(self.pattern)
        play = Pattern.value(self.play)

        if self.regularise:
            self.pos += play
            if self.pos >= 1:
                self.pos -= 1
                return value
        else:
            if self.rng.uniform(0, 1) < play:
                return value

        return None

class PFlipFlop(PStochasticPattern):
    """ PFlipFlop: flip a binary bit with some probability.
                   <initial> is initial value (0 or 1)
                   <p_on> is chance of switching from 0->1
                   <p_off> is chance of switching from 1->0

        >>> p = PFlipFlop(0, 0.9, 0.5)
        >>> p.nextn(16)
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        """

    def __init__(self, initial=0, p_on=0.5, p_off=0.5):
        super().__init__()
        self.initial = initial
        self.value = initial
        self.p_on = p_on
        self.p_off = p_off

    def reset(self):
        super().reset()
        self.value = self.initial

    def __next__(self):
        self.value = Pattern.value(self.value)
        self.p_on = Pattern.value(self.p_on)
        self.p_off = Pattern.value(self.p_off)

        if self.value == 0:
            if self.rng.uniform(0, 1) < self.p_on:
                self.value = 1
        else:
            if self.rng.uniform(0, 1) < self.p_off:
                self.value = 0

        return self.value


class PSwitchOne(PStochasticPattern):
    """ PSwitchOne: Capture `length` input values; loop, repeatedly switching two adjacent values.
        """

    def __init__(self, pattern, length=4):
        super().__init__()
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
            index = self.rng.randint(0, len(self.values)) - 1
            indexP = (index + 1) % len(self.values)
            self.values[index], self.values[indexP] = self.values[indexP], self.values[index]
            self.pos = 0

        rv = self.values[self.pos]
        self.pos += 1
        return rv
