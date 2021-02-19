import sys
import math
import copy
import random
import itertools

from .core import Pattern
from ..chord import Chord
from ..constants import INTERPOLATION_NONE, INTERPOLATION_LINEAR, INTERPOLATION_COSINE
from functools import reduce
from .chance import PStochasticPattern

import logging

log = logging.getLogger(__name__)

class PSequence(Pattern):
    """ Sequence: Sequence of values based on an array
        Takes an input list, and repeats the items in this list.

        >>> p = PSeq([ 1, 2, 3, 5 ])
        >>> p.nextn(10)
        [1, 2, 3, 5, 1, 2, 3, 5, 1, 2, 3, 5, 1, 2, 3, 5]
        """

    def __init__(self, sequence=[], repeats=sys.maxsize):
        #------------------------------------------------------------------------
        # take a copy of the list to avoid changing the original
        #------------------------------------------------------------------------
        if not hasattr(sequence, "__getitem__"):
            raise ValueError("Sequence must take a list argument")
        self.sequence = copy.copy(sequence)
        self.repeats = repeats

        self.reset()

    def reset(self):
        super().reset()
        self.rcount = 0
        self.pos = 0

    def __next__(self):
        # support for pattern arguments
        sequence = self.value(self.sequence)
        repeats = self.value(self.repeats)

        if len(sequence) == 0 or self.rcount >= repeats:
            raise StopIteration

        rv = Pattern.value(sequence[self.pos])
        self.pos += 1
        if self.pos >= len(sequence):
            self.pos = 0
            self.rcount += 1

        return rv

# Backwards-compatbility
PSeq = PSequence

class PSeries(Pattern):
    """ PSeries: Arithmetic series, beginning at `start`, increment by `step`

        >>> p = PSeries(3, 9)
        >>> p.nextn(16)
        [3, 12, 21, 30, 39, 48, 57, 66, 75, 84, 93, 102, 111, 120, 129, 138]
        """

    def __init__(self, start=0, step=1, length=sys.maxsize):
        self.start = start
        self.value = start
        self.step = step
        self.length = length
        self.count = 0

    def reset(self):
        super().reset()

        self.value = self.start
        self.count = 0

    def __next__(self):
        length = Pattern.value(self.length)
        if self.count >= length:
            # return None
            raise StopIteration
        step = Pattern.value(self.step)
        n = self.value
        self.value += step
        self.count += 1
        return n

class PRange(Pattern):
    """ PRange: Similar to PSeries, but specify a max/step value.

        >>> p = PRange(0, 20, 2)
        >>> p.nextn(16)
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        """

    def __init__(self, start=0, end=128, step=1):
        """
        Args:
            start (int or float): Start value
            end (int, float or Pattern): End value
            step (int, float or Pattern): Step value
        """
        self.start = start
        self.end = end
        self.step = step
        self.reset()

    def reset(self):
        super().reset()
        self.value = self.start

    def __next__(self):
        end = Pattern.value(self.end)
        step = Pattern.value(self.step)
        if step > 0 and self.value >= end:
            raise StopIteration
        elif step < 0 and self.value <= end:
            raise StopIteration
        rv = self.value
        self.value += step
        return rv

class PGeom(Pattern):
    """ PGeom: Geometric series, beginning at `start`, multiplied by `step`

        >>> p = PGeom(1, 2)
        >>> p.nextn(16)
        [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
        """

    def __init__(self, start=1, multiply=2, length=sys.maxsize):
        self.start = start
        self.value = start
        self.multiply = multiply
        self.length = length
        self.count = 0

    def reset(self):
        super().reset()
        self.value = self.start
        self.count = 0

    def __next__(self):
        if self.count >= self.length:
            raise StopIteration

        multiply = Pattern.value(self.multiply)

        rv = self.value
        self.value *= multiply
        self.count += 1
        return rv

class PImpulse(Pattern):
    """ PImpulse: Outputs a 1 every <period> events, otherwise 0.

        >>> p = PImpulse(4)
        >>> p.nextn(16)
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        """

    def __init__(self, period):
        self.period = period
        self.pos = 0

    def reset(self):
        super().reset()
        self.pos = 0

    def __next__(self):
        period = Pattern.value(self.period)

        if self.pos >= period:
            self.pos = 0

        if self.pos == 0:
            rv = 1
        else:
            rv = 0
        self.pos += 1

        return rv

class PLoop(Pattern):
    """ PLoop: Repeats a finite `pattern` for `n` repeats.
        Useful for pattern generators which don't natively loop.

        Input must be finite or results may vary.

        >>> p = PLoop(PSeq([ 1, 4, 9 ], 1))
        >>> p.nextn(16)
        [1, 4, 9, 1, 4, 9, 1, 4, 9, 1, 4, 9, 1, 4, 9, 1]
        """

    def __init__(self, pattern, count=sys.maxsize):
        self.pattern = pattern
        self.count = count
        self.pos = 0
        self.loop_index = 0
        self.read_all = False
        self.values = []

    def reset(self):
        super().reset()
        self.pos = 0
        self.loop_index = 0
        self.read_all = False
        self.values = []

    def __next__(self):
        if not self.read_all:
            try:
                value = next(self.pattern)
                self.values.append(value)
            except StopIteration:
                self.read_all = True

        if self.read_all and self.pos >= len(self.values):
            if self.loop_index >= self.count - 1:
                raise StopIteration
            else:
                self.loop_index += 1
                self.pos = 0

        rv = self.values[self.pos]
        self.pos += 1
        return rv

class PPingPong(Pattern):
    """ PPingPong: Ping-pong input pattern back and forth N times.

        >>> p = PPingPong(PSeq([ 1, 4, 9 ], 1), 10)
        >>> p.nextn(16)
        [1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4]
        """

    def __init__(self, pattern, count=1):
        self.pattern = pattern
        self.count = count
        self.reset()

    def reset(self):
        super().reset()
        self.pattern.reset()
        self.values = self.pattern.all()
        self.pos = 0
        self.dir = 1
        self.rpos = 0

    def __next__(self):
        if self.pos == 1 and self.rpos >= self.count:
            raise StopIteration

        rv = self.values[self.pos]
        self.pos += self.dir
        if self.pos == len(self.values) - 1:
            self.dir = -1
        elif self.pos == 0:
            self.dir = 1
            self.rpos += 1

        return rv

class PCreep(Pattern):
    """ PCreep: Loop `length`-note segment, progressing `creep` notes after `repeats` repeats.

        >>> p = PCreep(PSeries(), 3, 1, 2)
        >>> p.nextn(16)
        [0, 1, 2, 0, 1, 2, 1, 2, 3, 1, 2, 3, 2, 3, 4, 2]
        """

    def __init__(self, pattern, length=4, creep=1, repeats=1, prob=1):
        self.pattern = pattern
        self.length = length
        self.creep = creep
        self.repeats = repeats
        self.prob = prob
        self.reset()

    def reset(self):
        super().reset()
        self.buffer = []
        self.pos = 0
        self.rcount = 1
        while len(self.buffer) < self.length:
            self.buffer.append(next(self.pattern))

    def __next__(self):
        length = Pattern.value(self.length)
        creep = Pattern.value(self.creep)
        repeats = Pattern.value(self.repeats)
        prob = Pattern.value(self.prob)

        while len(self.buffer) < length:
            self.buffer.append(next(self.pattern))
        while len(self.buffer) > length:
            self.buffer.pop(0)

        if self.pos >= len(self.buffer):
            repeat = random.uniform(0, 1) < prob

            if self.rcount >= repeats or not repeat:
                #------------------------------------------------------------------------
                # finished creeping, pull some more data from our buffer
                #------------------------------------------------------------------------
                for n in range(creep):
                    self.buffer.pop(0)
                    self.buffer.append(next(self.pattern))
                self.rcount = 1
            else:
                #------------------------------------------------------------------------
                # finished the Nth repeat but, still more repeats to do
                #------------------------------------------------------------------------
                self.rcount += 1

            #------------------------------------------------------------------------
            # reset to the start of our buffer
            #------------------------------------------------------------------------
            if not repeat:
                self.pos -= 1
            else:
                self.pos = 0

        self.pos += 1
        return self.buffer[self.pos - 1]

class PStutter(Pattern):
    """ PStutter: Play each note of `pattern` `count` times.
        Is really a more convenient way to do:

            PCreep(pattern, 1, 1, count)

        >>> p = PStutter(PSeries(), 2)
        >>> p.nextn(16)
        [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]
        """

    def __init__(self, pattern, count=2):
        self.pattern = pattern
        self.count = count
        self.count_current = Pattern.value(count)
        self.pos = self.count_current
        self.value = 0

    def __next__(self):
        if self.pos >= self.count_current:
            self.count_current = Pattern.value(self.count)
            self.value = next(self.pattern)
            self.pos = 0
        self.pos += 1
        return self.value

class PSubsequence(Pattern):
    """ PSubsequence: Returns a finite subsequence of an input pattern.

        >>> p = PSubsequence(...)
        >>> p.nextn(16)
        """

    def __init__(self, pattern, offset, length):
        self.pattern = pattern
        self.offset = offset
        self.length = length
        self.pos = 0
        self.values = []

    def reset(self):
        super().reset()
        self.pos = 0

    def __next__(self):
        offset = Pattern.value(self.offset)
        length = Pattern.value(self.length)

        if self.pos >= length:
            raise StopIteration

        while len(self.values) <= self.pos + offset:
            self.values.append(next(self.pattern))

        rv = self.values[offset + self.pos]
        self.pos += 1

        return rv

class PInterpolate(Pattern):
    def __init__(self, pattern, steps, interpolation=INTERPOLATION_LINEAR):
        self.pattern = pattern
        self.steps = steps
        self.interpolation = interpolation
        self.reset()

    def reset(self):
        super().reset()
        self.value = next(self.pattern)
        self.step_values = [self.value]
        self.pos = 0

    def __next__(self):
        if self.pos == len(self.step_values):
            vsteps = int(Pattern.value(self.steps))

            #--------------------------------------------------------------------------------
            # Special case in which next step duration is zero: set the target value
            # instantly, and pull a new target value.
            #--------------------------------------------------------------------------------
            while vsteps == 0:
                self.value = next(self.pattern)
                vsteps = int(Pattern.value(self.steps))
            target = next(self.pattern)

            #--------------------------------------------------------------------------------
            # Calculate interpolated values.
            #--------------------------------------------------------------------------------
            if self.interpolation == INTERPOLATION_NONE:
                self.step_values = list(self.value for n in range(vsteps - 1)) + [target]
            elif self.interpolation == INTERPOLATION_LINEAR:
                dt = target - self.value
                self.step_values = list(self.value + dt * (n + 1) / vsteps for n in range(vsteps))
            elif self.interpolation == INTERPOLATION_COSINE:
                dt = target - self.value
                self.step_values = list(self.value + dt * 0.5 * (1.0 - math.cos(math.pi * (n + 1) / vsteps))
                                        for n in range(vsteps))
            else:
                raise ValueError("Interpolation type not recognised")
            self.pos = 0

        self.value = self.step_values[self.pos]
        self.pos += 1
        return self.value

class PReverse(Pattern):
    """ PReverse: Reverses a finite sequence. """

    def __init__(self, input):
        self.input = input
        self.reset()

    def reset(self):
        super().reset()
        self.values = reversed(list(self.input))

    def __next__(self):
        return next(self.values)

class PReset(Pattern):
    """ PReset: Resets `pattern` whenever `trigger` is true

        >>> p = PReset(PSeries(0, 1), PImpulse(4))
        >>> p.nextn(16)
        [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
        """

    def __init__(self, pattern, trigger):
        self.pattern = pattern
        self.trigger = trigger

    def __next__(self):
        trigger_input = next(self.trigger)
        if trigger_input is not None and trigger_input > 0:
            self.pattern.reset()

        return next(self.pattern)

class PCounter(Pattern):
    """ PCounter: Increments a counter by 1 for each zero-crossing in `trigger`.

        >>> p = PCounter(PImpulse(4))
        >>> p.nextn(16)
        [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        """

    def __init__(self, trigger):
        self.trigger = trigger
        self.value = 0
        self.count = 0

    def __next__(self):
        value = next(self.trigger)
        if value > 0 and self.value <= 0:
            self.count += 1
            self.value = value
        elif value <= 0 and self.value > 0:
            self.value = value

        return self.count

class PCollapse(Pattern):
    """ PCollapse: Skip over any rests in `input` """

    def __init__(self, input):
        self.input = input

    def __next__(self):
        rv = None
        while rv is None:
            rv = Pattern.value(self.input)
        return rv

class PNoRepeats(Pattern):
    """ PNoRepeats: Skip over repeated values in `input` """

    def __init__(self, input):
        self.input = input
        self.value = sys.maxsize

    def __next__(self):
        rv = sys.maxsize
        while rv == self.value or rv == sys.maxsize:
            rv = Pattern.value(self.input)
        self.value = rv
        return rv

class PPad(Pattern):
    """ PPad: Pad `pattern` with rests until it reaches length `length`.
        """

    def __init__(self, pattern, length):
        self.pattern = pattern
        self.length = length
        self.reset()

    def reset(self):
        super().reset()
        self.count = 0

    def __next__(self):
        try:
            rv = next(self.pattern)
        except StopIteration:
            if self.count >= self.length:
                raise StopIteration
            rv = None

        self.count += 1
        return rv

class PPadToMultiple(Pattern):
    """ PPadToMultiple: Pad `pattern` with rests until its length is divisible by `multiple`.
        Enforces a minimum padding of `minimum_pad`.

        Useful to create patterns which occupy a whole number of bars.
        """

    def __init__(self, pattern, multiple, minimum_pad=0):
        self.pattern = pattern
        self.multiple = multiple
        self.minimum_pad = minimum_pad
        self.count = 0
        self.padcount = 0
        self.terminated = False

    def __next__(self):
        try:
            rv = next(self.pattern)
        except StopIteration:
            if self.padcount >= self.minimum_pad and (self.count % self.multiple == 0):
                raise StopIteration
            else:
                rv = None
                self.padcount += 1

        self.count += 1
        return rv

class PArpeggiator(PStochasticPattern):
    """ PArpeggiator: Arpeggiator.

        <type> can be one of:
            PArp.UP
            PArp.DOWN
            PArp.UPDOWN
            PArp.CONVERGE
            PArp.DIVERGE
            PArp.RANDOM

        >>> p = PLoop(PArpeggiator(Chord.major, PArpeggiator.CONVERGE))
        >>> p.nextn(16)
        [0, 12, 4, 7, 0, 12, 4, 7, 0, 12, 4, 7, 0, 12, 4, 7]
        """
    UP = 0
    DOWN = 1
    CONVERGE = 2
    DIVERGE = 3
    RANDOM = 4

    def __init__(self, chord=Chord.major, type=UP):
        super().__init__()

        self.chord = chord
        self.type = type
        self.pos = 0
        self.offsets = []

        try:
            #------------------------------------------------------------------------
            # prefer to specify a chord (or Key)
            #------------------------------------------------------------------------
            self._notes = self.chord.semitones
        except AttributeError:
            #------------------------------------------------------------------------
            # can alternatively specify a list of notes
            #------------------------------------------------------------------------
            self._notes = self.chord

        self.restart()

    def get_notes(self):
        return self._notes

    def set_notes(self, notes):
        self._notes = list(sorted(notes))

    notes = property(get_notes, set_notes)

    def restart(self):
        self._notes = list(sorted(self._notes))

        if self.type == PArpeggiator.UP:
            self.offsets = list(range(len(self._notes)))
        elif self.type == PArpeggiator.DOWN:
            self.offsets = list(reversed(list(range(len(self._notes)))))
        elif self.type == PArpeggiator.CONVERGE:
            self.offsets = [(n // 2) if (n % 2 == 0) else (0 - (n + 1) // 2) for n in range(len(self._notes))]
        elif self.type == PArpeggiator.DIVERGE:
            if len(self._notes) % 2 == 0:
                self.offsets = [(len(self._notes) // 2 - 1) - (n // 2) if (n % 2 == 0) else
                                (len(self._notes) // 2 + n // 2) for n in range(len(self.notes))]
            else:
                self.offsets = [(len(self._notes) // 2 - 1) - (n // 2) if (n % 2 == 1) else
                                (len(self._notes) // 2 + n // 2) for n in range(len(self.notes))]
        elif self.type == PArpeggiator.RANDOM:
            self.offsets = list(range(len(self._notes)))
            self.rng.shuffle(self.offsets)
        else:
            raise ValueError("Invalid Arpeggiator type: %s" % self.type)

    def reset(self):
        super().reset()
        self.restart()

    def __next__(self):
        if len(self._notes) == 0:
            self.pos = 0
            return None

        pos = self.value(self.pos)

        if pos < len(self.offsets) and pos < len(self._notes):
            offset = self.offsets[pos]
            rv = self._notes[offset]
            self.pos = pos + 1
            return rv
        else:
            # self.pos = 0
            # self.restart()
            # return next(self)
            # TODO: Looping arpeggiator
            raise StopIteration

class PEuclidean(Pattern):
    """ PEuclidean: Generate Euclidean rhythms.
        Effectively tries to space <mod> events out evenly over `length` beats.
        Events returned are either 1 or None (rest)

        >>> p = PEuclidean(5, 8)
        >>> p.nextn(8)
        [1, None, 1, 1, None, 1, 1, None]
        """

    def __init__(self, mod, length, phase=0):
        self.mod = mod
        self.length = length
        self.sequence = []
        self.pos = phase

    def __next__(self):
        length = self.value(self.length)
        mod = self.value(self.mod)
        sequence = self._euclidean(length, mod)
        if self.pos >= len(sequence):
            self.pos = 0
        rv = sequence[self.pos]
        self.pos += 1
        return rv

    def _split_remainder(self, seq):
        """
        Assuming an input array of the form [a, a, a, a, b, b, b],
        partitions the input into two halves and returns
        ([a, a, a, a], [b, b, b])
        """
        last = None
        a = []
        b = []
        for value in seq:
            if last is None or value == last:
                a.append(value)
                last = value
            else:
                b.append(value)
        return (a, b)

    def _interleave(self, a, b):
        """
        Assuming two input arrays of the form ([a, a, a, a], [b, b, b]),
        interleaves the two with concatenation and returns
        ([ab, ab, ab, a])
        """
        if len(a) < len(b):
            return [a[n] + b[n] for n in range(len(a))] + b[len(a) - len(b):]
        elif len(b) < len(a):
            return [a[n] + b[n] for n in range(len(b))] + a[len(b) - len(a):]
        else:
            return [a[n] + b[n] for n in range(len(b))]

    def _euclidean(self, length, mod):
        """ Implements Bjorklund's algorithm, described in Toussaint (2005):
        http://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf
        """

        seqs = [(1,)] * mod + [(None,)] * (length - mod)
        seqs, remainder = self._split_remainder(seqs)
        while True:
            if len(remainder) <= 1:
                break
            seqs = self._interleave(seqs, remainder)
            seqs, remainder = self._split_remainder(seqs)

        return reduce(lambda a, b: a + b, seqs + remainder)

class PExplorer(Pattern):
    def __init__(self, density=0.5, length=4, length_min=2, length_max=6, value_max=12, jump_max=4, loop=None):
        self.density = density
        self.length = length
        self.length_min = length_min
        self.length_max = length_max
        self.value_max = value_max
        self.jump_max = jump_max
        self.loop = loop
        self.reset()

    def reset(self):
        super().reset()
        self.counter = 0
        self.loop_pos = 0
        self.values = []
        self._generate_values()

    def _generate_values(self):
        self.values = []
        value_last = None
        for n in range(self.length):
            if random.uniform(0, 1) < self.density:
                if value_last is None:
                    value = random.randint(0, self.value_max)
                else:
                    value = value_last + random.randint(-self.jump_max, self.jump_max)
                if value < 0:
                    value = 0
                if value > self.value_max:
                    value = self.value_max
                self.values.append(value)
                value_last = value
            else:
                self.values.append(None)

    def explore(self):
        OP_MUTATE = 0
        OP_ROTATE = 1
        OP_SWAP = 2
        OP_SPLIT = 3
        OP_REVERSE = 4
        OP_DELETE = 5
        OP_INSERT = 6
        OP_COPY = 7

        OPERATION_NAMES = ["mutate", "rotate", "swap", "split", "reverse", "delete", "insert", "copy"]

        log.debug("PExplorer: Exploring: %s" % self.values)
        operations = [OP_MUTATE, OP_ROTATE, OP_SWAP, OP_SPLIT, OP_REVERSE, OP_DELETE, OP_INSERT, OP_COPY]

        values = self.values
        if len(values) >= self.length_max:
            operations.remove(OP_INSERT)
            operations.remove(OP_COPY)
        if len(values) <= self.length_min:
            operations.remove(OP_DELETE)
        operation = random.choice(operations)
        log.debug("PExplorer: Selected operation: %s" % OPERATION_NAMES[operation])

        #------------------------------------------------------------------------
        # MUTATE: Replace a note with another note found within the sequence.
        #------------------------------------------------------------------------
        if operation == OP_MUTATE:
            filled_indices = [n[0] for n in filter(lambda n: n[1] is not None, list(enumerate(values)))]
            if len(filled_indices) > 0:
                index = random.choice(filled_indices)
                values[index] = random.randint(0, self.value_max)

        #------------------------------------------------------------------------
        # ROTATE: Rotate the sequence forwards or backwards one slot.
        #------------------------------------------------------------------------
        elif operation == OP_ROTATE:
            if random.uniform(0, 1) < 0.1:
                values = values[-1:] + values[:-1]
            else:
                values = values[1:] + values[:1]

        #------------------------------------------------------------------------
        # SWAP: Exchange two notes.
        #------------------------------------------------------------------------
        elif operation == OP_SWAP:
            indexA = random.randint(0, len(values) - 1)
            indexB = (indexA + 1) % len(values)
            values[indexA], values[indexB] = values[indexB], values[indexA]

        #------------------------------------------------------------------------
        # SPLIT: Cut sequence in half and swap parts.
        #------------------------------------------------------------------------
        elif operation == OP_SPLIT:
            point = random.randint(1, len(values) - 1)
            values = values[:point] + values[point:]

        #------------------------------------------------------------------------
        # REVERSE: Reverses the sequence.
        #------------------------------------------------------------------------
        elif operation == OP_REVERSE:
            values = list(reversed(values))

        #------------------------------------------------------------------------
        # DELETE: Remove an item.
        #------------------------------------------------------------------------
        elif operation == OP_DELETE:
            index = random.randrange(len(values))
            del (values[index])

        #------------------------------------------------------------------------
        # INSERT: Insert a new value at random.
        #------------------------------------------------------------------------
        elif operation == OP_INSERT:
            index = random.randint(0, len(values))
            value = random.choice(list(range(self.value_max + 1)) + [None])
            values.insert(index, value)

        #------------------------------------------------------------------------
        # COPY: Duplicate a note at the subsequent index.
        #------------------------------------------------------------------------
        elif operation == OP_COPY:
            index = random.randint(0, len(values) - 1)
            values.insert(index + 1, values[index])

        log.debug("PExplorer: New values: %s" % values)

        self.values = values
        self.counter = 0
        return self

    def __next__(self):
        if self.counter >= len(self.values):
            if self.loop is None:
                raise StopIteration
            else:
                self.loop_pos += 1
                if self.loop_pos >= self.loop:
                    self.explore()
                    self.loop_pos = 0
                self.counter = 0

        rv = self.values[self.counter]
        self.counter += 1
        return rv

class PPermut(Pattern):
    """ PPermut: Generate every permutation of `count` input items.

        >>> p = PPermut(PSeq([ 1, 11, 111, 1111 ]), 4)
        >>> p.nextn(16)
        [1, 11, 111, 1111, 1, 11, 1111, 111, 1, 111, 11, 1111, 1, 111, 1111, 11]
        """

    def __init__(self, input, count=8):
        if not hasattr(input, "__next__"):
            raise ValueError("Input to PPermut must be a Pattern or other iterator")
        self.input = input
        self.count = count
        self.pos = sys.maxsize
        self.permindex = sys.maxsize
        self.permutations = []

    def reset(self):
        super().reset()
        self.pos = sys.maxsize
        self.permindex = sys.maxsize
        self.permutations = []

    def __next__(self):
        if self.permindex > len(self.permutations):
            n = 0
            values = []
            while n < self.count:
                try:
                    v = next(self.input)
                except StopIteration:
                    break

                values.append(v)
                n += 1

            self.permutations = list(itertools.permutations(values))
            self.permindex = 0
            self.pos = 0
        elif self.pos >= len(self.permutations[0]):
            self.permindex = self.permindex + 1
            self.pos = 0

        if self.permindex >= len(self.permutations):
            raise StopIteration

        rv = self.permutations[self.permindex][self.pos]
        self.pos += 1
        return rv

class PPatternGeneratorAction(Pattern):
    """ PPatternGeneratorAction: Each time its pattern is exhausted, request a new pattern by calling <fn>.

        >>>
        >>>
        """

    def __init__(self, fn):
        self.fn = fn
        self.pattern = self.fn()

    def __next__(self):
        try:
            return next(self.pattern)
        except StopIteration:
            self.pattern = self.fn()
            # if not self.pattern:
            # causes this to break horribly in the PStaticSeq case
            # -- seems to try to evaluate self.pattern as a list
            if self.pattern is None:
                raise StopIteration
            return next(self)

PDecisionPoint = PPatternGeneratorAction

class PSequenceAction(Pattern):
    """ PSequenceAction: Iterate over an array, perform a function, and repeat.

        >>>
        >>>
        """

    def __init__(self, list, fn, repeats=sys.maxsize):
        self.list = list
        self.list_orig = list
        self.sequence = PSequence(self.list, 1)
        self.fn = fn
        self.repeats = repeats
        self.repeat_counter = 0

    def reset(self):
        super().reset()
        self.list = self.list_orig
        self.sequence = PSequence(self.list, 1)
        self.repeat_counter = 0

    def __next__(self):
        try:
            return next(self.sequence)
        except StopIteration:
            repeats = Pattern.value(self.repeats)
            self.repeat_counter += 1
            if self.repeat_counter >= repeats:
                raise StopIteration
            self.list = self.fn(self.list)
            self.sequence = PSequence(self.list, 1)
            return next(self)

class PMetropolis(Pattern):
    def __init__(self, notes, repeats, rests):
        self.notes = notes
        self.repeats = repeats
        self.rests = rests
        self.note_index = 0
        self.note_offset = 0

    def __next__(self):
        repeats = self.repeats
        if len(repeats) < len(self.notes):
            repeats = repeats * int(math.ceil(len(self.notes) / len(repeats)))
        rests = self.rests
        if len(rests) < len(self.notes):
            rests = rests * int(math.ceil(len(self.notes) / len(rests)))

        if self.note_offset > repeats[self.note_index] + rests[self.note_index]:
            self.note_index += 1
            self.note_offset = 0
        if self.note_index >= len(self.notes):
            self.note_index = 0
            self.note_offset = 0

        if self.note_offset < repeats[self.note_index]:
            rv = self.notes[self.note_index]
        else:
            rv = None

        self.note_offset += 1
        return rv

