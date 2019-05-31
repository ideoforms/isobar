"""Testing pydoc"""

import sys
import copy
import random
import itertools

from isobar.pattern.core import *
from isobar.key import *
from isobar.util import *
from isobar.chord import *
from functools import reduce

class PSeq(Pattern):
    """ PSeq: Sequence of values based on an array
        Takes an input list, and repeats the items in this list.

        >>> p = PSeq([ 1, 2, 3, 5 ])
        >>> p.nextn(10)
        [1, 2, 3, 5, 1, 2, 3, 5, 1, 2, 3, 5, 1, 2, 3, 5]
        """

    def __init__(self, list = [], repeats = sys.maxsize):
        #------------------------------------------------------------------------
        # take a copy of the list to avoid changing the original
        #------------------------------------------------------------------------
        assert hasattr(list, "__getitem__"), "PSeq must take a list argument"
        self.list = copy.copy(list)
        self.repeats = repeats

        self.reset()

    def reset(self):
        self.rcount = 0
        self.pos = 0

    def __next__(self):
        if len(self.list) == 0 or self.rcount >= self.repeats:
            raise StopIteration

        # support for pattern arguments
        list = self.value(self.list)
        repeats = self.value(self.repeats)

        rv = Pattern.value(list[self.pos])
        self.pos += 1
        if self.pos >= len(list):
            self.pos = 0
            self.rcount += 1

        return rv

class PSeries(Pattern):
    """ PSeries: Arithmetic series, beginning at <start>, increment by <step>

        >>> p = PSeries(3, 9)
        >>> p.nextn(16)
        [3, 12, 21, 30, 39, 48, 57, 66, 75, 84, 93, 102, 111, 120, 129, 138]
        """

    def __init__(self, start = 0, step = 1, length = sys.maxsize):
        self.start = start
        self.value = start
        self.step = step
        self.length = length
        self.count = 0

    def reset(self):
        self.value = self.start 
        self.count = 0

        Pattern.reset(self)

    def __next__(self):
        if self.count >= self.length:
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

    def __init__(self, start = 0, end = 128, step = 1):
        self.start = start
        self.end = end
        self.step = step
        self.reset()

    def reset(self):
        self.value = self.start 

        Pattern.reset(self)

    def __next__(self):
        step = Pattern.value(self.step)
        if step > 0 and self.value >= self.end:
            raise StopIteration
        elif step < 0 and self.value <= self.end:
            raise StopIteration
        rv = self.value
        self.value += step
        return rv

class PGeom(Pattern):
    """ PGeom: Geometric series, beginning at <start>, multiplied by <step>

        >>> p = PGeom(1, 2)
        >>> p.nextn(16)
        [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
        """

    def __init__(self, start = 1, multiply = 2, length = sys.maxsize):
        self.start = start
        self.value = start
        self.multiply = multiply
        self.length = length
        self.count = 0

    def reset(self):
        self.value = self.start 
        self.count = 0

        Pattern.reset(self)

    def __next__(self):
        if self.count >= self.length:
            raise StopIteration

        multiply = Pattern.value(self.multiply)

        rv = self.value
        self.value *= multiply
        self.count += 1
        return rv

class PLoop(Pattern):
    """ PLoop: Repeats a finite <pattern> for <n> repeats.
        Useful for pattern generators which don't natively loop.

        Input must be finite or results may vary.

        >>> p = PLoop(PSeq([ 1, 4, 9 ], 1))
        >>> p.nextn(16)
        [1, 4, 9, 1, 4, 9, 1, 4, 9, 1, 4, 9, 1, 4, 9, 1]
        """

    def __init__(self, pattern, count = sys.maxsize, bang = False):
        self.pattern = pattern
        self.count = count
        self.bang = bang
        self.reset()

    def reset(self):
        self.pos = 0
        self.rpos = 1
        self.read_all = False
        self.values = []

        Pattern.reset(self)

    def __next__(self):
        # print "%d, %d, %d" % (self.rebang, self.pos, self.rpos)
        if self.bang and self.pos >= len(self.values) and self.rpos >= self.count:
            self.reset()
            self.pattern.bang()

        if not self.read_all:
            # print "reading all"
            try:
                rv = next(self.pattern)
                self.values.append(rv)
            except StopIteration:
                self.read_all = True

        if self.read_all and self.pos >= len(self.values):
            if self.rpos >= self.count:
                raise StopIteration
            else:
                self.rpos += 1
                self.pos = 0

        # print "pos = %d, value len = %d" % (self.pos, len(self.values))
        rv = self.values[self.pos]
        self.pos += 1
        return rv

class PConcat(Pattern):
    """ PConcat: Concatenate the output of multiple finite sequences

        >>> PConcat([ PSeq([ 1, 2, 3], 2), PSeq([ 9, 8, 7 ], 2) ]).nextn(16)
        [1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4]
        """

    def __init__(self, inputs):
        self.inputs = inputs
        self.current = inputs.pop(0)

    def __next__(self):
        try:
            return next(self.current)
        except StopIteration:
            if len(self.inputs) > 0:
                self.current = self.inputs.pop(0)
                # can't just blindly return the first value of current
                # -- what if it is empty? 
                return next(self)
            else:
                # no more sequences left, so just return.
                raise StopIteration

class PPingPong(Pattern):
    """ PPingPong: Ping-pong input pattern back and forth N times.

        >>> p = PPingPong(PSeq([ 1, 4, 9 ], 1), 10)
        >>> p.nextn(16)
        [1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4, 1, 4, 9, 4]
        """

    def __init__(self, pattern, count = 1):
        self.pattern = pattern
        self.count = count
        self.reset()

    def reset(self):
        self.pattern.reset()
        self.values = self.pattern.all()
        self.pos = 0
        self.dir = 1
        self.rpos = 0

    def __next__(self):
        if self.pos == 0 and self.rpos >= self.count:
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
    """ PCreep: Loop <length>-note segment, progressing <creep> notes after <count> repeats.

        >>> p = PCreep(PSeries(), 3, 1, 2)
        >>> p.nextn(16)
        [0, 1, 2, 0, 1, 2, 1, 2, 3, 1, 2, 3, 2, 3, 4, 2]
        """
    def __init__(self, pattern, length = 4, creep = 1, count = 1, prob = 1):
        self.pattern = pattern
        self.length = length
        self.creep = creep
        self.count = count
        self.prob = prob

        self.buffer = []
        self.pos = 0
        self.rcount = 1
        while len(self.buffer) < length:
            self.buffer.append(next(pattern))

    def __next__(self):
        pos     = Pattern.value(self.pos)
        length  = Pattern.value(self.length)
        creep   = Pattern.value(self.creep)
        count   = Pattern.value(self.count)
        prob    = Pattern.value(self.prob)

        while len(self.buffer) < length:
                self.buffer.append(next(self.pattern))
        while len(self.buffer) > length:
                self.buffer.pop(0)

        if self.pos >= len(self.buffer):
            repeat = random.uniform(0, 1) < prob

            if self.rcount >= count or not repeat:
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
    """ PStutter: Play each note of <pattern> <count> times.
        Is really a more convenient way to do:

            PCreep(pattern, 1, 1, count)

        >>> p = PStutter(PSeries(), 2)
        >>> p.nextn(16)
        [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]
        """

    def __init__(self, pattern, count = 2):   
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

class PWrap(Pattern):
    """ PWrap: Wrap input note values within <min>, <max>.

        >>> p = PWrap(PSeries(5, 3), 0, 10)
        >>> p.nextn(16)
        [5, 8, 1, 4, 7, 0, 3, 6, 9, 2, 5, 8, 1, 4, 7, 0]
        """

    def __init__(self, pattern, min = 40, max = 80):
        self.pattern = pattern
        self.min = min
        self.max = max

    def __next__(self):
        value = next(self.pattern)
        while value < self.min:
            value += self.max - self.min
        while value >= self.max:
            value -= self.max - self.min
        return value

class PPermut(Pattern):
    """ PPermut: Generate every permutation of <count> input items.

        >>> p = PPermut(PSeq([ 1, 11, 111, 1111 ]), 4)
        >>> p.nextn(16)
        [1, 11, 111, 1111, 1, 11, 1111, 111, 1, 111, 11, 1111, 1, 111, 1111, 11]
        """

    def __init__(self, input, count = 8):
        self.input = input
        self.count = count
        self.pos = sys.maxsize
        self.permindex = sys.maxsize
        self.permutations = []

    def reset(self):
        self.pos = sys.maxsize
        self.permindex = sys.maxsize
        self.permutations = []

        Pattern.reset(self)

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

class PDegree(Pattern):
    """ PDegree: Map scale index <degree> to MIDI notes in <scale>.

        >>> p = PDegree(PSeries(0, 1), Scale.major)
        >>> p.nextn(16)
        [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26]
        """
    def __init__(self, degree, scale = Scale.major):
        self.degree = degree
        self.scale = scale

    def __next__(self):
        degree = Pattern.value(self.degree)
        scale = Pattern.value(self.scale)
        if degree is None:
            return None

        return scale[degree]

class PMidiToFrequency(Pattern):
    """ PMidiToFrequency: Map MIDI note to frequency value.
        """
    def __init__(self, note):
        self.note = note

    def __next__(self):
        note = Pattern.value(self.note)
        return miditofreq(note)

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
        self.pos = 0

        Pattern.reset(self)

    def __next__(self):
        offset = Pattern.value(self.offset)
        length = Pattern.value(self.length)

        # print "length is %d, pos %d" % (length, self.pos)
        if self.pos >= length:
            raise StopIteration

        while len(self.values) <= self.pos + offset:
            self.values.append(next(self.pattern))

        rv = self.values[offset + self.pos]
        self.pos += 1

        return rv

class PImpulse(Pattern):
    """ PImpulse: Outputs a 1 every <period> events, otherwise 0.

        >>> p = PImpulse(4)
        >>> p.nextn(16)
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        """
    def __init__(self, period):
        self.period = period
        self.pos = period

    def reset(self):
        self.pos = 0
    
    def __next__(self):
        period = self.value(self.period)

        if self.pos >= period - 1:
            rv = 1
            self.pos = 0
        else:
            rv = 0
            self.pos += 1

        return rv

class PReset(Pattern):
    """ PReset: Resets <pattern> each time it receives a zero-crossing from
                <trigger>

        >>> p = PReset(PSeries(0, 1), PImpulse(4))
        >>> p.nextn(16)
        [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
        """
    def __init__(self, pattern, trigger):
        self.value = 0
        self.pattern = pattern
        self.trigger = trigger

    def reset(self):
        self.value = 0

    def __next__(self):
        value = next(self.trigger)
        if value > 0 and self.value <= 0:
            self.pattern.reset()
            self.value = value
        elif value <= 0 and self.value > 0:
            self.value = value

        return next(self.pattern)
    
class PCounter(Pattern):
    """ PCounter: Increments a counter by 1 for each zero-crossing in <trigger>.

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

class PArp(Pattern):
    """ PArp: Arpeggiator.

        <type> can be one of:
            PArp.UP
            PArp.DOWN
            PArp.UPDOWN
            PArp.CONVERGE
            PArp.DIVERGE
            PArp.RANDOM

        >>> p = PLoop(PArp(Chord.major, PArp.CONVERGE))
        >>> p.nextn(16)
        [0, 12, 4, 7, 0, 12, 4, 7, 0, 12, 4, 7, 0, 12, 4, 7]
        """
    UP = 0
    DOWN = 1
    CONVERGE = 2
    DIVERGE = 2
    RANDOM = 3

    def __init__(self, chord = Chord.major, type = UP):
        self.chord = chord
        self.type = type
        self.pos = 0
        self.offsets = []

        try:
            #------------------------------------------------------------------------
            # prefer to specify a chord (or Key)
            #------------------------------------------------------------------------
            self.notes = self.chord.semitones
        except:
            #------------------------------------------------------------------------
            # can alternatively specify a list of notes
            #------------------------------------------------------------------------
            self.notes = self.chord

        if type == PArp.UP:
            self.offsets = list(range(len(self.notes)))
        elif type == PArp.DOWN:
            self.offsets = list(reversed(list(range(len(self.notes)))))
        elif type == PArp.CONVERGE:
            self.offsets = [ (n / 2) if (n % 2 == 0) else (0 - (n + 1) / 2) for n in range(len(self.notes)) ]
        elif type == PArp.DIVERGE:
            self.offsets = [ (n / 2) if (n % 2 == 0) else (0 - (n + 1) / 2) for n in range(len(self.notes)) ]
            self.offsets = list(reversed(self.offsets))
        elif type == PArp.RANDOM:
            self.offsets = list(range(len(self.notes)))
            random.shuffle(self.offsets)

    def __next__(self):
        type = self.value(self.type)
        pos = self.value(self.pos)

        if pos < len(self.offsets):
            offset = self.offsets[pos]
            rv = self.notes[offset]
            self.pos = pos + 1
            return rv
        else:
            raise StopIteration

class PEuclidean(Pattern):
    """ PEuclidean: Generate Euclidean rhythms.
        Effectively tries to space <mod> events out evenly over <length> beats.
        Events returned are either 1 or None (rest)

        >>> p = PEuclidean(5, 8)
        >>> p.nextn(8)
        [1, None, 1, 1, None, 1, 1, None]
        """
    def __init__(self, mod, length, phase = 0):
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
        if len(a) < len(b):
            return [ a[n] + b[n] for n in range(len(a)) ] + b[len(a) - len(b):]
        elif len(b) < len(a):
            return [ a[n] + b[n] for n in range(len(b)) ] + a[len(b) - len(a):]
        else:
            return [ a[n] + b[n] for n in range(len(b)) ]

    def _euclidean(self, length, mod):
        """ Implements Bjorklund's algorithm, described in Toussaint (2005):
        http://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf
        """

        seqs = [ (1,) ] * mod + [ (None,) ] * (length - mod)
        seqs, remainder = self._split_remainder(seqs)
        while True:
            if len(remainder) <= 1:
                break
            seqs = self._interleave(seqs, remainder)
            seqs, remainder = self._split_remainder(seqs)

        return reduce(lambda a, b: a + b, seqs + remainder)

class PDecisionPoint(Pattern):
    """ PDecisionPoint: Each time its pattern is exhausted, requests a new pattern by calling <fn>.

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
                return None
            return next(self)

