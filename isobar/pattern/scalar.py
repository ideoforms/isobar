from __future__ import annotations
from .core import Pattern
from .sequence import PSeries
from ..util import scale_lin_exp, scale_lin_lin

from typing import Callable

class PChanged(Pattern):
    """ PChanged: Outputs a 1 if the value of the input pattern has changed,
        or 0 otherwise.

        >>> a = PSequence([1, 0, 1, 2, 2, 2, 1, 0, 0, 1], repeats=1)
        >>> b = PChanged(a)
        >>> b.all()
        [1, 1, 1, 0, 0, 1, 1, 0, 1]
        """

    def __init__(self, source: Pattern):
        self.source = source
        self.current = Pattern.value(self.source)

    def __repr__(self):
        return ("PChanged(%s)" % repr(self.source))

    def reset(self):
        super().reset()
        self.current = Pattern.value(self.source)

    def __next__(self):
        next = Pattern.value(self.source)
        rv = 0 if next == self.current else 1
        self.current = next
        return rv

class PDiff(Pattern):
    """ PDiff: Outputs the difference between the current and previous values of an input pattern
        If the current or next value are None, a value of None will be output.

        The length of the output pattern is always 1 less than the length of the input.

        >>> a = PSequence([1, 0, 1, 2, 2, 2, 1, 0, 0, 1], repeats=1)
        >>> b = PDiff(a)
        >>> b.all()
        [-1, 1, 1, 0, 0, -1, -1, 0, 1]
        """

    def __init__(self, source: Pattern):
        self.source = source
        self.current = Pattern.value(self.source)

    def __repr__(self):
        return ("PDiff(%s)" % repr(self.source))

    def reset(self):
        super().reset()
        self.current = Pattern.value(self.source)

    def __next__(self):
        next = Pattern.value(self.source)
        if self.current is None or next is None:
            rv = None
        else:
            rv = next - self.current
        self.current = next
        return rv

class PSkipIf(Pattern):
    """ PSkipIf: If `skip` is false, returns `input`; otherwise, returns None.
        """

    def __init__(self, pattern: Pattern, skip: bool):
        self.pattern = pattern
        self.skip = skip

    def __repr__(self):
        return ("PSkipIf(%s, %s)" % (repr(self.pattern), self.skip))

    def __next__(self):
        rv = Pattern.value(self.pattern)
        rskip = Pattern.value(self.skip)
        if rskip:
            rv = None
        return rv

class PNormalise(Pattern):
    """ PNormalise: Adaptively normalise `input` to [0..1] over a linear scale.
        Use maximum and minimum values found in history.

        If you know the output range ahead of time, use `PScaleLinLin`.
        """

    def __init__(self, input: Pattern):
        self.input = input

        self.lower = None
        self.upper = None
        self.history = []

    def __repr__(self):
        return ("PNormalise(%s)" % repr(self.input))

    def __next__(self):
        value = Pattern.value(self.input)

        if self.lower is None:
            self.lower = value
            self.upper = value
        else:
            if value > self.upper:
                self.upper = value
            if value < self.lower:
                self.lower = value

        if self.upper == self.lower:
            rv = 0.0
        else:
            rv = (value - self.lower) / (self.upper - self.lower)

        return rv

class PMap(Pattern):
    """ PMap: Apply an arbitrary function to an input pattern.
              Will pass any additional arguments, which can also be patterns.
              Instances of None in the input stream will be passed through to
              the function as normal.

        >>> PMap(PSeries(), lambda value: value * value).nextn(16)
        [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]

        >>> PMap(PSeries(), pow, PSeries()).nextn(16)
        [1, 1, 4, 27, 256, 3125, 46656, 823543, 16777216, 387420489, 10000000000, ... ]
        """

    def __init__(self, input: Pattern, operator: Callable, *args, **kwargs):
        self.input = input
        self.operator = operator
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return ("PMap(%s, %s, %s, %s)" % (repr(self.input), repr(self.operator), repr(self.args), repr(self.kwargs)))

    def reset(self):
        super().reset()
        for arg in self.args:
            if isinstance(arg, Pattern):
                arg.reset()
        for arg in self.kwargs.values():
            if isinstance(arg, Pattern):
                arg.reset()

    def __next__(self):
        args = [Pattern.value(value) for value in self.args]
        kwargs = dict((key, Pattern.value(value)) for key, value in list(self.kwargs.items()))
        value = next(self.input)
        rv = self.operator(value, *args, **kwargs)
        return rv

class PMapEnumerated(PMap):
    """ PMapEnumerated: Apply arbitrary function to input, passing a counter.

        >>> PMapEnumerated(PSeq([ 1, 11, 111 ]), lambda n, value: n * value).nextn(16)
        [0, 11, 222, 3, 44, 555, 6, 77, 888, 9, 110, 1221, 12, 143, 1554, 15]
        """

    def __init__(self, *args):
        self.args = args
        PMap.__init__(self, *args)
        self.counter = PSeries()

    def __repr__(self):
        return ("PMapEnumerated(%s)" % repr(self.args))

    def __next__(self):
        args = [Pattern.value(value) for value in self.args]
        kwargs = dict((key, Pattern.value(value)) for key, value in list(self.kwargs.items()))
        value = next(self.input)
        rv = self.operator(next(self.counter), value, *args, **kwargs)
        return rv

class PScaleLinLin(PMap):
    """ PScaleLinLin: Map `input` from linear range [a,b] to linear range [c,d].

        >>> p = PScaleLinLin(PWhite(), 0, 1, -50, 50)
        >>> p.nextn(16)
        [-34.434991496625955, -33.38823791706497, 42.153457333940267, 16.692545937573783, ... -48.850511242044604 ]
        """

    def __init__(self, input: Pattern, *args):
        super().__init__(input, scale_lin_lin, *args)

class PScaleLinExp(PMap):
    """ PScaleLinExp: Map `input` from linear range [a,b] to exponential range [c,d].

        >>> p = PScaleLinExp(PWhite(0.0, 1.0), 0, 1, 40, 20000)
        >>> p.nextn(16)
        [946.888, 282.944, 2343.145, 634.637, 218.844, 19687.330, 4457.627, 172.419, 934.666, ... 46.697 ]
        """

    def __init__(self, input: Pattern, *args):
        super().__init__(input, scale_lin_exp, *args)

class PRound(PMap):
    """ PRound: Round `input` to N decimal places.

        >>> p = PRound(PWhite(0.0, 10.0))
        >>> p.nextn(16)
        [6, 8, 6, 0, 7, 6, 6, 4, 7, 7, 8, 7, 6, 8, 8, 4]
        """

    def round(self, value, *args):
        if value is None:
            return None
        else:
            return round(value, *args)

    def __init__(self, input, *args):
        PMap.__init__(self, input, self.round, *args)

class PScalar(PMap):
    """ PScalar: Reduce tuples and lists into single scalar values,
        either by taking the mean or the first value.
        Empty lists are reduced to None.

        >>> p = PScalar(PSequence([ 1, (2, 3), (4, 5, 6), (), 7 ], 1)
        >>> p.all())
        [1, 2.5, 5, None, 7]
        """

    def scalar(self, pattern: Pattern, method: str):
        value = Pattern.value(pattern)
        try:
            values = list(value)
            if len(values) == 0:
                return None
            else:
                if method == "mean":
                    return sum(values) / len(values)
                elif method == "first":
                    return values[0]
                else:
                    raise ValueError("Invalid scalar reduction method: %s" % method)
        except TypeError:
            return value

    def __init__(self, pattern: Pattern, method: str = "mean"):
        """
        Args:
            input (Pattern): Input pattern
            method (str): Can be "mean", which returns the mean of each list; or
                          "first", which returns the first item in each list.
        """
        PMap.__init__(self, pattern, self.scalar, method=method)

class PWrap(Pattern):
    """ PWrap: Wrap input note values within <min>, <max>.

        >>> p = PWrap(PSeries(5, 3), 0, 10)
        >>> p.nextn(16)
        [5, 8, 1, 4, 7, 0, 3, 6, 9, 2, 5, 8, 1, 4, 7, 0]
        """

    def __init__(self, pattern: Pattern, min: int = 40, max: int = 80):
        self.pattern = pattern
        self.min = min
        self.max = max

    def __repr__(self):
        return ("PWrap(%s, %s, %s)" % (repr(self.pattern), self.min, self.max))

    def __next__(self):
        value = next(self.pattern)
        while value < self.min:
            value += self.max - self.min
        while value >= self.max:
            value -= self.max - self.min
        return value

class PIndexOf(Pattern):
    """ PIndexOf: Find index of items from `pattern` in <list>

        >>> p = PIndexOf([ chr(ord("a") + n) for n in range(26) ], PSeq("isobar"))
        >>> p.nextn(16)
        [8, 18, 14, 1, 0, 17, 8, 18, 14, 1, 0, 17, 8, 18, 14, 1]
        """

    def __init__(self, list: Pattern, item):
        self.list = list
        self.item = item

    def __repr__(self):
        return ("PIndexOf(%s, %s)" % (repr(self.list), repr(self.item)))

    def __next__(self):
        list = Pattern.value(self.list)
        item = Pattern.value(self.item)
        if list is None or item is None or item not in list:
            return None
        return list.index(item)
