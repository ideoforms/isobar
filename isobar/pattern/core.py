#-------------------------------------------------------------------------------
# isobar: a python library for expressing and manipulating musical patterns.
#-------------------------------------------------------------------------------

from __future__ import annotations
import copy
import inspect
from typing import Iterable, Callable, Any, TYPE_CHECKING
from ..timelines.lfo import LFO

import isobar

class Pattern:
    """ Pattern: Abstract superclass of all pattern generators.

        Patterns are at the core of isobar. A Pattern implements the iterator
        protocol, representing a sequence of values which are iteratively
        returned by the next() method. A pattern may be finite, after which
        point it raises a StopIteration exception. Call reset() to return
        a pattern to its initial state.

        Patterns can be subject to standard arithmetic operators as expected.
        """

    LENGTH_MAX = 65536

    def __repr__(self):
        # Used in place of a common string representation
        return "Pattern()"

    def __len__(self):
        # formerly defined as len(list(self)), but list(self) seemingly relies
        # on a correct __len__ to function as expected.
        items = self.all()
        return len(items)

    def __neg__(self):
        return 0 - self

    def __abs__(self):
        """ Absolute value. """
        return PAbs(self)

    def __add__(self, operand):
        """Binary op: add two patterns"""
        return PAdd(self, operand)

    def __radd__(self, operand):
        """Binary op: add two patterns"""
        return self.__add__(operand)

    def __sub__(self, operand):
        """Binary op: subtract two patterns"""
        return PSub(self, operand)

    def __rsub__(self, operand):
        """Binary op: subtract two patterns"""
        return PSub(operand, self)

    def __mul__(self, operand):
        """Binary op: multiply two patterns"""
        return PMul(self, operand)

    def __rmul__(self, operand):
        """Binary op: multiply two patterns"""
        return self.__mul__(operand)

    def __truediv__(self, operand):
        """Binary op: divide two patterns"""
        return PDiv(self, operand)

    def __rtruediv__(self, operand):
        """Binary op: divide two patterns"""
        return PDiv(operand, self)

    def __floordiv__(self, operand):
        """Binary op: integer divide two patterns"""
        return PFloorDiv(self, operand)

    def __rfloordiv__(self, operand):
        """Binary op: integer divide two patterns"""
        return PFloorDiv(operand, self)

    def __mod__(self, operand):
        """Modulo"""
        return PMod(self, operand)

    def __rmod__(self, operand):
        """Modulo (as operand)"""
        operand = Pattern.pattern(operand)
        return operand.__mod__(self)

    def __pow__(self, operand):
        """Power"""
        return PPow(self, operand)

    def __rpow__(self, operand):
        """Power (as operand)"""
        operand = Pattern.pattern(operand)
        return operand.__pow__(self)

    def __lshift__(self, operand):
        """Left bitshift"""
        return PLShift(self, operand)

    def __rlshift__(self, operand):
        """Left bitshift"""
        return PLShift(operand, self)

    def __rshift__(self, operand):
        """Right bitshift"""
        return PRShift(self, operand)

    def __rrshift__(self, operand):
        """Right bitshift"""
        return PRShift(operand, self)

    def __eq__(self, operand):
        """ Equal """
        return PEqual(self, operand)

    def __ne__(self, operand):
        """ Not equal """
        return PNotEqual(self, operand)

    def __gt__(self, operand):
        """ Greater than """
        return PGreaterThan(self, operand)

    def __ge__(self, operand):
        """ Greater than or equal """
        return PGreaterThanOrEqual(self, operand)

    def __lt__(self, operand):
        """ Less than """
        return PLessThan(self, operand)

    def __le__(self, operand):
        """ Less than or equal """
        return PLessThanOrEqual(self, operand)

    def __and__(self, operand):
        """ And """
        return PAnd(self, operand)

    def __iter__(self):
        return self

    def poll(self, on: bool = True) -> object:
        """
        If set, causes the Pattern object to output its value to stdout each time
        its __next__() method is called.

        Returns the Pattern object, useful when scheduling like so:

        timeline.schedule({
            "note": pattern.poll(),
            ...
        })

        Args:
            on: Whether to poll the Pattern's output.

        Returns:
            The Pattern.
        """
        if not hasattr(self.__class__, "__next_orig__"):
            self.__class__.__next_orig__ = self.__class__.__next__

        def _get_and_print_next(self):
            value = self.__next_orig__()
            if hasattr(self, "_poll") and self._poll:
                print("%s: %s" % (self.__class__.__name__, value))
            return value

        self.__class__.__next__ = _get_and_print_next
        self._poll = on
        return self

    def nextn(self, count: int) -> list:
        """
        Returns the next `count` output values.
        If fewer than `count` values are generated, return all output values.
        """
        rv = []
        try:
            for n in range(count):
                rv.append(next(self))
        except StopIteration:
            pass

        return rv

    def __next__(self):
        raise StopIteration

    def all(self, maximum: int = LENGTH_MAX) -> list:
        """
        Returns all output values, up to a maximum length of `maximum`.
        """
        values = []
        try:
            # do we even need a LENGTH_MAX?
            # if we omit it, .all() will become an alias for list(pattern)
            #  - maybe not such a bad thing.
            for n in range(maximum):
                value = next(self)
                values.append(value)
        except StopIteration:
            pass

        self.reset()
        return values

    def reset(self):
        """ Calling reset() should always reset a Pattern back to its initial state
            immediately after construction.

            When implementing new Patterns, this may require storing some state variables
            to be stored.
        """
        fields = vars(self)
        for name, field in list(fields.items()):
            if isinstance(field, Pattern):
                field.reset()
            #------------------------------------------------------------------------
            # look through list items and reset anything in here too
            # (needed to reset items in PConcat)
            #------------------------------------------------------------------------
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, Pattern):
                        item.reset()
            elif isinstance(field, dict):
                for item in list(field.values()):
                    if isinstance(item, Pattern):
                        item.reset()

    def append(self, other: Pattern) -> PConcatenate:
        """
        Returns a new pattern with the contents of `other` appended to the contents of `self`.
        """
        return PConcatenate([self, other])

    @property
    def timeline(self):
        """
        Returns the timeline that this Pattern is embedded in, if any.
        """
        stack = inspect.stack()
        for frame in stack:
            frameobj = frame[0]
            args, _, _, value_dict = inspect.getargvalues(frameobj)
            if len(args) and args[0] == 'self':
                instance = value_dict.get('self', None)
                classname = instance.__class__.__name__
                if classname == "Timeline":
                    return instance

    def copy(self) -> Pattern:
        """
        Returns a copy of this Pattern.
        """
        return copy.deepcopy(self)

    @staticmethod
    def value(v):
        """
        Resolve a pattern to a scalar value (that is, the next item in this
        pattern, recursively).
        """
        if isinstance(v, Pattern):
            return Pattern.value(next(v))
        # Should lists/dicts be handled similarly?
        elif isinstance(v, tuple):
            return tuple(Pattern.value(element) for element in v)
        else:
            return v

    @staticmethod
    def pattern(v):
        """
        Patternify a value, turning it into an object with a next() method
        to obtain its next value.

        Pattern subclasses remain untouched.
        Scalars and other objects are turned into PConstant objects. """

        if isinstance(v, Pattern):
            return v
        elif isinstance(v, LFO):
            return PLFO(v)
        elif isinstance(v, dict):
            return isobar.PDict(v)
        elif isinstance(v, str):
            from isobar.notation import parse_notation

            try:
                return parse_notation(v)
            except ValueError:
                return isobar.PConstant(v)
        else:
            return isobar.PConstant(v)

class PConstant(Pattern):
    """ PConstant: Returns a fixed value.

        >>> p = PConstant(4)
        >>> p.nextn(16)
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        """

    def __init__(self, constant: float):
        self.constant = constant

    def __repr__(self):
        return ("PConstant(%s)" % repr(self.constant))

    def __next__(self):
        return self.constant

    def __float__(self):
        return float(self.constant)

class PRef(Pattern):
    """ PRef: Contains a reference to another pattern, which can be replaced dynamically.
        Returns the next value of the pattern contained.
        Useful to change an inner pattern in real time.
        """

    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    def __repr__(self):
        return ("PRef(%s)" % repr(self.pattern))

    def set_pattern(self, pattern: Pattern):
        """ Replace the referenced pattern with another. """
        self.pattern = pattern

    def __next__(self):
        return next(self.pattern)

class PFunc(Pattern):
    """ PFunc: Returns the value generated by a function.
        Useful to incorporate additional logic into a pattern.

        >>> seconds = PFunc(lambda: datetime.datetime.now().second)
        >>> p.nextn(16)
        [19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19]"""

    def __init__(self, function: Callable):
        self.function = function

    def __repr__(self):
        return ("PFunc(%s)" % repr(self.function))

    def __next__(self):
        function = Pattern.value(self.function)
        return function()

class PArrayIndex(Pattern):
    """ PArrayIndex: Request a specified index from an array.
        If the item is a Pattern, the next value from that pattern is returned.
        """

    def __init__(self, list: Iterable, index: int):
        self.list = list
        self.index = index

    def __repr__(self):
        return ("PArrayIndex(%s, %s)" % (self.list, self.index))

    def __next__(self):
        list = Pattern.value(self.list)
        index = Pattern.value(self.index)

        #------------------------------------------------------------------
        # null indices denote a rest -- so return a null value.
        # (same behaviour as PDegree: a degree of None returns a rest.)
        #------------------------------------------------------------------
        if index is None:
            return None
        else:
            index = int(index)
            return Pattern.value(list[index])

class PDict(Pattern):
    """ PDict: Construct a pattern from a dict of arrays, or an array of dicts.
        The below are equivalent:

            PDict([ { "note" : 60, "velocity" : 64 }, { "note" : 67, "velocity" : 32 }, ... ])
            PDict({ "note" : [ 60, 67 ], "velocity" : [ 64, 32 ]})

        Thanks to Dan Stowell <http://www.mcld.co.uk/>
        """

    def __init__(self, value: dict = None):
        from .sequence import PSequence

        self.dict = {}

        if type(value) == dict:
            #------------------------------------------------------------------------
            # Value is a dict of arrays.
            #------------------------------------------------------------------------
            self.dict = dict([(k, Pattern.pattern(v)) for k, v in value.items()])
        elif type(value) == list:
            #------------------------------------------------------------------------
            # Value is an array of dicts.
            #------------------------------------------------------------------------
            self.dict = {}
            try:
                keys = list(value[0].keys())
                for key in keys:
                    self.dict[key] = PSequence([item[key] for item in value], 1)
            except IndexError:
                pass

    def __getattr__(self, key: str):
        """
        Implemented for syntactical sugar, so that a track's params property
        can be modified by doing (e.g.) track.params.cutoff = 200
        """
        if key == "dict" or key.startswith("__"):
            return super().__getattr__(key)
        else:
            return self.dict[key]

    def __setattr__(self, key: str, value: Any):
        if key == "dict" or key.startswith("__"):
            return super().__setattr__(key, value)
        else:
            self.dict[key] = value

    def __repr__(self):
        return ("PDict(%s)" % repr(self.dict))

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]

    def __contains__(self, key):
        return key in self.dict

    def load(self, filename: str, quantize: float = None):
        """
        Load pattern data from a MIDI file.

        Args:
            filename (str): Filename to read from (.mid)
        """
        from isobar.io.midifile import MidiFileInputDevice
        reader = MidiFileInputDevice(filename)
        self.dict = reader.read(quantize=quantize)

    def save(self, filename: str):
        """
        Save pattern data to a MIDI file.

        Args:
            filename (str): Filename to write to (.mid)
            quantize (float): Quantization level. 1.0 = quantize to beat, 0.25 = quantize to quarter-beat, etc.
        """
        from isobar.io.midifile import MidiFileOutputDevice
        writer = MidiFileOutputDevice(filename)
        clock = isobar.DummyClock()
        timeline = isobar.Timeline(self, output_device=writer, clock_source=clock)
        timeline.schedule(self)
        timeline.stop_when_done = True
        try:
            clock.run()
        except StopIteration:
            pass
        writer.write()

    def has_key(self, key):
        return key in self.dict

    def setdefault(self, key, value):
        if key not in self.dict:
            self.dict[key] = value

    def keys(self) -> list:
        return list(self.dict.keys())

    def values(self) -> list:
        return list(self.dict.values())

    def items(self) -> list:
        return list(self.dict.items())

    def __next__(self):
        vdict = Pattern.value(self.dict)

        #--------------------------------------------------------------------------------
        # This previously raised a StopIteration, but this breaks the common case in
        # which an empty params dict is bound to the timeline:
        #
        # timeline.schedule({ "patch": FooPatch, "params": {} }) <- ends immediately
        #
        # So instead simply return the empty dict in this case.
        # This will also return `None` when Pattern.value(dict) evaluates to None.
        # Hopefully this doesn't break any cases in the wild...
        #--------------------------------------------------------------------------------
        # if not vdict:
        #     return vdict

        #--------------------------------------------------------------------------------
        # Doing a list comprehension without surrounding square brackets produces a lazy
        # evaluation, which causes the inner StopIteration to be suppressed. We want to
        # explicitly raise it, so greedily evaluate the dict.
        #--------------------------------------------------------------------------------
        rv = dict([(k, Pattern.value(vdict[k])) for k in vdict])

        return rv

class PDictKey(Pattern):
    """ PDictKey: Request a specified key from a dictionary.
        """

    def __init__(self, dict: dict, key):
        self.dict = dict
        self.key = key

    def __repr__(self):
        return ("PDictKey(%s, %s)" % (repr(self.dict), repr(self.key)))

    def __next__(self):
        vdict = Pattern.value(self.dict)
        vkey = Pattern.value(self.key)
        return vdict[vkey]

class PConcatenate(Pattern):
    """ PConcatenate: Concatenate the output of multiple sequences.

        >>> PConcatenate([ PSequence([ 1, 2, 3 ], 2), PSequence([ 9, 8, 7 ], 2) ]).nextn(16)
        [1, 2, 3, 1, 2, 3, 9, 8, 7, 9, 8, 7]
        """

    def __init__(self, inputs: list):
        self.inputs = inputs
        self.pos = 0

    def __repr__(self):
        return ("PConcatenate(%s)" % self.inputs)

    def __next__(self):
        try:
            return next(self.inputs[self.pos])
        except StopIteration:
            if self.pos < len(self.inputs) - 1:
                self.pos += 1
                return next(self)
            else:
                # no more sequences left, so just return.
                raise StopIteration

    def reset(self):
        super().reset()
        self.pos = 0

class PAbs(Pattern):
    """ PAbs: Absolute value of `input` """

    def __init__(self, input):
        self.input = input

    def __repr__(self):
        return ("PAbs(%s)" % repr(self.input))

    def __next__(self):
        next = Pattern.value(self.input)
        if next is not None:
            return abs(next)
        return next

class PInt(Pattern):
    """ PInt: Integer value of `input` """

    def __init__(self, input: int):
        self.input = input

    def __repr__(self):
        return ("PInt(%s)" % self.input)

    def __next__(self):
        next = Pattern.value(self.input)
        if next is not None:
            return int(next)
        return next

class PLFO(Pattern):
    """ PLFO: Encapsulates an LFO object.
    """
    def __init__(self, lfo: LFO):
        self.lfo = lfo
    
    def __repr__(self):
        return ("PLFO(%s)" % repr(self.lfo))

    def __next__(self):
        return self.lfo.value

#------------------------------------------------------------------
# Binary operators
#------------------------------------------------------------------

class PBinOp(Pattern):
    def __init__(self, a, b):
        self.a = a
        self.b = b

class PAdd(PBinOp):
    """ PAdd: Add elements of two patterns (shorthand: patternA + patternB) """

    def __str__(self):
        return "%s + %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a + b

class PSub(PBinOp):
    """ PSub: Subtract elements of two patterns (shorthand: patternA - patternB) """

    def __str__(self):
        return "%s - %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a - b

class PMul(PBinOp):
    """ PMul: Multiply elements of two patterns (shorthand: patternA * patternB) """

    def __str__(self):
        return "(%s) * (%s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a * b

class PDiv(PBinOp):
    """ PDiv: Divide elements of two patterns (shorthand: patternA / patternB) """

    def __str__(self):
        return "(%s) / (%s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a / b

class PFloorDiv(PBinOp):
    """ PFloorDiv: Integer division (shorthand: patternA // patternB) """

    def __str__(self):
        return "(%s) // (%s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a // b

class PMod(PBinOp):
    """ PMod: Modulo elements of two patterns (shorthand: patternA % patternB) """

    def __str__(self):
        return "(%s) %% (%s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a % b

class PPow(PBinOp):
    """ PPow: One pattern to the power of another (shorthand: patternA ** patternB) """

    def __str__(self):
        return "pow(%s, %s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else pow(a, b)

class PLShift(PBinOp):
    """ PLShift: Binary left-shift (shorthand: patternA << patternB) """

    def __str__(self):
        return "(%s << %s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a << b

class PRShift(PBinOp):
    """ PRShift: Binary right-shift (shorthand: patternA << patternB) """

    def __str__(self):
        return "(%s >> %s)" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a >> b

class PEqual(PBinOp):
    """ PEqual: Return 1 if a == b, 0 otherwise (shorthand: patternA == patternB) """

    def __str__(self):
        return "%s == %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a == b

class PNotEqual(PBinOp):
    """ PGreaterThanOrEqual: Return 1 if a != b, 0 otherwise (shorthand: patternA != patternB) """

    def __str__(self):
        return "%s != %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a != b

class PGreaterThan(PBinOp):
    """ PGreaterThan: Return 1 if a > b, 0 otherwise (shorthand: patternA > patternB) """

    def __str__(self):
        return "%s > %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a > b

class PGreaterThanOrEqual(PBinOp):
    """ PGreaterThanOrEqual: Return 1 if a >= b, 0 otherwise (shorthand: patternA >= patternB) """

    def __str__(self):
        return "%s >= %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a >= b

class PLessThan(PBinOp):
    """ PLessThan: Return 1 if a < b, 0 otherwise (shorthand: patternA < patternB) """

    def __str__(self):
        return "%s < %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a < b

class PLessThanOrEqual(PBinOp):
    """ PLessThanOrEqual: Return 1 if a <= b, 0 otherwise (shorthand: patternA <= patternB) """

    def __str__(self):
        return "%s <= %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return None if a is None or b is None else a <= b

class PAnd(PBinOp):
    """ PAnd: Return True if a and b, False otherwise (shorthand: patternA & patternB) """

    def __str__(self):
        return "%s & %s" % (self.a, self.b)

    def __next__(self):
        a = Pattern.value(self.a)
        b = Pattern.value(self.b)
        return True if a and b else False
