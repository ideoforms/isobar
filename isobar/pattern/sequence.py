"""Testing pydoc"""

import sys
import random
import itertools

from isobar.pattern.core import *
from isobar.key import *
from isobar.util import *

class PConst(Pattern):
    """Pattern: Constant value"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "constant"

    def next(self):
        return self.value

class PSeq(Pattern):
    """Pattern: Fixed sequence"""
    def __init__(self, list = [], repeats = sys.maxint):
        self.list = list
        self.repeats = repeats

        self.rcount = 0
        self.pos = 0

    def next(self):
        if len(self.list) == 0 or self.rcount >= self.repeats:
            return None

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
    """Pattern: Arithmetic series"""

    def __init__(self, start = 0, step = 1, length = sys.maxint):
        self.value = start
        self.step = step
        self.length = length
        self.count = 0

    def next(self):
        if self.count >= self.length:
            return None
            # raise StopIteration
        n = self.value
        # XXX need a general-use way of writing this
        step = self.step.next() if isinstance(self.step, Pattern) else self.step
        self.value += step
        self.count += 1
        return n

class PLoop(Pattern):
    def __init__(self, pattern, count = sys.maxint):
        self.pattern = pattern
        self.values = []
        self.count = count
        self.pos = 0
        self.rpos = 1
        self.read_all = False

    def next(self):
        if not self.read_all:
            rv = self.pattern.next()
            if rv is None:
                self.read_all = True
            else:
                self.values.append(rv)

        if self.read_all and self.pos >= len(self.values):
            if self.rpos >= self.count:
                return None
            else:
                self.rpos += 1
                self.pos = 0

        rv = self.values[self.pos]
        self.pos += 1
        return rv

# might also be nice to have a "repeats" param
# (in which case, PStutter could also be written as PCreep(p, 1, 1, n)
class PCreep(Pattern):
    def __init__(self, pattern, length = 4, creep = 1, count = 1):
        self.pattern = pattern
        self.length = length
        self.creep = creep
        self.count = count
        self.buffer = []
        self.pos = 0
        self.rcount = 1
        while len(self.buffer) < length:
            self.buffer.append(pattern.next())

    def next(self):
        pos = self.value(self.pos)
        length = self.value(self.length)
        creep = self.value(self.creep)
        count = self.value(self.count)
        while len(self.buffer) < length:
                self.buffer.append(self.pattern.next())
        while len(self.buffer) > length:
                self.buffer.pop(0)

        if self.pos >= len(self.buffer):
            if self.rcount >= count:
                for n in range(creep):
                    self.buffer.pop(0)
                    self.buffer.append(self.pattern.next())
                self.rcount = 1
            else:
                self.rcount += 1
            self.pos = 0

        self.pos += 1
        return self.buffer[self.pos - 1]

class PStutter(Pattern):
    def __init__(self, pattern, count = 2):   
        self.pattern = pattern
        self.count = count
        self.pos = count
        self.value = 0

    def next(self):
        if self.pos >= self.count:
            self.value = self.pattern.next()
            self.pos = 0
        self.pos += 1
        return self.value

class PWrap(Pattern):
    def __init__(self, pattern, min = 40, max = 80):
        self.pattern = pattern
        self.min = min
        self.max = max

    def next(self):
        value = self.pattern.next()
        while value < self.min:
            value += self.max - self.min
        while value > self.max:
            value -= self.max - self.min
        return value

class PPermut(Pattern):
    def __init__(self, input, count = 8):
        self.input = input
        self.count = count
        self.pos = sys.maxint
        self.permindex = sys.maxint
        self.permutations = []

    def next(self):
        if self.permindex > len(self.permutations):
            n = 0
            values = []
            while n < self.count:
                v = self.input.next()
                if v is None:
                    break
                values.append(v)
                n += 1

            permiter = itertools.permutations(values)
            self.permutations = []
            for n in permiter:
                self.permutations.append(n)

            self.permindex = 0
            self.pos = 0
        elif self.pos >= len(self.permutations[0]):
            self.permindex = self.permindex + 1
            self.pos = 0
            
        rv = self.permutations[self.permindex][self.pos]
        self.pos += 1
        return rv

class PDegree(Pattern):
    def __init__(self, degree, scale = Scale.major):
        self.degree = degree
        self.scale = scale

    def next(self):
        degree = self.value(self.degree)
        scale = self.value(self.scale)
        return scale[degree]

