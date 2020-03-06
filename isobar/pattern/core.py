#-------------------------------------------------------------------------------
# isobar: a python library for expressing and manipulating musical patterns.
#-------------------------------------------------------------------------------

import sys
import copy
import random
import inspect
import itertools

import isobar


class Pattern:
    """ Pattern: Abstract superclass of all pattern generators.

        Patterns are at the core of isoar. A Pattern implements the iterator
        protocol, representing a sequence of values which are iteratively
        returned by the next() method. A pattern may be finite, after which
        point it raises a StopIteration exception. Call reset() to return
        a pattern to its initial state.

        Patterns can be subject to standard arithmetic operators as expected.
        """

    LENGTH_MAX = 65536
    GENO_SEPARATOR = "/"

    def __init__(self):
        pass

    def __str__(self):
        return "pattern(%s)" % self.__class__

    def __len__(self):
        # formerly defined as len(list(self)), but list(self) seeminly relies
        # on a correct __len__ to function as expected.
        items = self.all()
        return len(items)

    def __neg__(self):
        return 0 - self

    def __add__(self, operand):
        """Binary op: add two patterns"""
        # operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
        # return PAdd(copy.deepcopy(self), operand)

        # we actually want to retain references to our constituent patterns
        # in case the user later changes parameters of one
        operand = Pattern.pattern(operand)
        return PAdd(self, operand)

    def __radd__(self, operand):
        """Binary op: add two patterns"""
        return self.__add__(operand)

    def __sub__(self, operand):
        """Binary op: subtract two patterns"""
        operand = Pattern.pattern(operand)
        return PSub(self, operand)

    def __rsub__(self, operand):
        """Binary op: subtract two patterns"""
        operand = Pattern.pattern(operand)
        return PSub(operand, self)

    def __mul__(self, operand):
        """Binary op: multiply two patterns"""
        operand = Pattern.pattern(operand)
        return PMul(self, operand)

    def __rmul__(self, operand):
        """Binary op: multiply two patterns"""
        return self.__mul__(operand)

    def __truediv__(self, operand):
        """Binary op: divide two patterns"""
        operand = Pattern.pattern(operand)
        return PDiv(self, operand)

    def __floordiv__(self, operand):
        """Binary op: divide two patterns"""
        operand = Pattern.pattern(operand)
        return PFloorDiv(self, operand)

    def __rdiv__(self, operand):
        """Binary op: divide two patterns"""
        return self.__div__(operand)

    def __mod__(self, operand):
        """Modulo"""
        operand = Pattern.pattern(operand)
        return PMod(self, operand)

    def __rmod__(self, operand):
        """Modulo (as operand)"""
        operand = Pattern.pattern(operand)
        return operand.__mod__(self)

    def __rpow__(self, operand):
        """Power (as operand)"""
        operand = Pattern.pattern(operand)
        return operand.__pow__(self)

    def __pow__(self, operand):
        """Power"""
        operand = Pattern.pattern(operand)
        return PPow(self, operand)

    def __lshift__(self, operand):
        """Left bitshift"""
        operand = Pattern.pattern(operand)
        return PLShift(self, operand)

    def __rshift__(self, operand):
        """Right bitshift"""
        operand = Pattern.pattern(operand)
        return PRShift(self, operand)

    def __iter__(self):
        return self

    def nextn(self, count):
        rv = []
        # can't do a naive [ self.next() for n in range(count) ]
        # as we want to catch StopIterations.
        try:
            for n in range(count):
                rv.append(next(self))
        except StopIteration:
            pass

        return rv

    def __next__(self):
        # default pattern should be void
        raise StopIteration

    def all(self):
        values = []
        try:
            # do we even need a LENGTH_MAX?
            # if we omit it, .all() will become an alias for list(pattern)
            #  - maybe not such a bad thing.
            for n in range(Pattern.LENGTH_MAX):
                value = next(self)
                values.append(value)
        except StopIteration:
            pass

        self.reset()
        return values

    def reset(self):
        """ reset a finite sequence back to position 0 """
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

    def append(self, other):
        return PConcat([ self, other ])

    @property
    def timeline(self):
        """ returns the timeline that i am embedded in, if any """
        stack = inspect.stack()
        for frame in stack:
            frameobj = frame[0]
            args, _, _, value_dict = inspect.getargvalues(frameobj)
            if len(args) and args[0] == 'self':
                instance = value_dict.get('self', None)
                classname = instance.__class__.__name__
                if classname == "Timeline":
                    return instance

    @staticmethod
    def fromgenotype(genotype):
        """ create a new object based on this genotype """
        parts = genotype.split(Pattern.GENO_SEPARATOR)
        classname = parts[0]
        arguments = parts[1:]
        try:
            classes = vars(isobar)
            classobj = classes[classname]
            instance = classobj()
            fields = vars(instance)
            counter = 0
            for name, field in list(fields.items()):
                instance.__dict__[name] = eval(arguments[counter])
                counter += 1
        except Exception as e:
            print(("fail: %s" % e))
            pass

        return instance

    def breedWith(self, other):
        """ XXX: we should probably have a Genotype class that deals with all this """

        genotypeA = self.genotype()
        genotypeB = other.genotype()
        genesA = genotypeA.split("/")[1:]
        genesB = genotypeB.split("/")[1:]
        genotype = [ genotypeA.split("/")[0] ]
        for n in range(len(genesA)):
            if random.uniform(0, 1) < 0.5:
                genotype.append(genesA[n])
            else:
                genotype.append(genesB[n])
        genotypeC = Pattern.GENO_SEPARATOR.join(genotype)
        print("A %s\nB %s\n> %s" % (genotypeA, genotypeB, genotypeC))
        return Pattern.fromgenotype(genotypeC)

    def genotype(self):
        """ return a string representation of this pattern, suitable for breeding """
        genotype = "%s" % (self.__class__.__name__)
        fields = vars(self)

        import base64

        for name, field in list(fields.items()):
            genotype += Pattern.GENO_SEPARATOR

            if isinstance(field, Pattern):
                genotype += "(%s)" % field.genotype()
            elif isinstance(field, str):
                genotype += base64.b64encode(field)
            else:
                genotype += str(field)

        return genotype

    def copy(self):
        return copy.deepcopy(self)

    @staticmethod
    def value(v):
        """ Resolve a pattern to its value (that is, the next item in this
            pattern, recursively).
            """
        return Pattern.value(next(v)) if isinstance(v, Pattern) else v

    @staticmethod
    def pattern(v):
        """ Patternify a value, turning it into an object with a next() method
        to obtain its next value.
        
        Pattern subclasses remain untouched.
        Lists are turned into PSeq sequences.
        Scalars and other objects are turned into PConst objects. """

        from isobar.pattern.sequence import PSeq

        if isinstance(v, Pattern):
            return v
        elif isinstance(v, list):
            return PSeq(v, 1)
        else:
            return PConst(v)

class PConst(Pattern):
    """ PConst: Pattern returning a fixed value

        >>> p = PConst(4)
        >>> p.nextn(16)
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        """
    def __init__(self, constant):
        self.constant = constant

    def __str__(self):
        return "constant"

    def __next__(self):
        return self.constant

class PRef(Pattern):
    """ PRef: Pattern containing a reference to another pattern
        Returns the next value of the pattern contained.
        Useful to change an inner pattern in real time.
        """
    def __init__(self, pattern):
        self.pattern = pattern

    def change(self, pattern):
        self.pattern = pattern

    def __next__(self):
        return next(self.pattern)

class PFunc(Pattern):
    def __init__(self, fn):
        self.fn = fn

    def __next__(self):
        fn = Pattern.value(self.fn)
        return fn()

class PDict(Pattern):
    """ PDict: Construct a pattern from a dict of arrays, or an array of dicts.
        The below are equivalent:

            PDict([ { "note" : 60, "velocity" : 64 }, { "note" : 67, "velocity" : 32 }, ... ])
            PDict({ "note" : [ 60, 67 ], "velocity" : [ 64, 32 ]})

        Thanks to Dan Stowell <http://www.mcld.co.uk/>
        """
    def __init__(self, value = None):
        from isobar.pattern.sequence import PSeq

        self.dict = {}

        if type(value) == dict:
            #------------------------------------------------------------------------
            # Value is a dict of arrays.
            #------------------------------------------------------------------------
            self.dict = value
        elif type(value) == list:
            #------------------------------------------------------------------------
            # Value is an array of dicts.
            #------------------------------------------------------------------------
            self.dict = {}
            try:
                keys = list(value[0].keys())
                for key in keys:
                    self.dict[key] = PSeq([ item[key] for item in value ], 1)
            except IndexError:
                pass

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __contains__(self, key):
        return key in self.dict

    @classmethod
    def load(self, filename):
        from isobar.io.midifile import MidiFileIn
        from isobar.pattern.sequence import PSeq

        reader = MidiFileIn()
        d = reader.read(filename)
        d = dict([ (key, PSeq(value, 1)) for key, value in list(d.items()) ])
        return PDict(d)

    def has_key(self, key):
        return key in self.dict

    def setdefault(self, key, value):
        if not key in self.dict:
            self.dict[key] = value

    def keys(self):
        return list(self.dict.keys())

    def values(self):
        return list(self.dict.values())

    def items(self):
        return list(self.dict.items())

    def __next__(self):
        vdict = Pattern.value(self.dict)
        if not vdict:
            raise StopIteration

        # for some reason, doing a list comprehension without the surrounding square
        # brackets causes an inner StopIteration to be suppressed -- we want to
        # explicitly raise it.
        rv = dict([ (k, Pattern.value(vdict[k])) for k in vdict ])

        return rv

class PIndex(Pattern):
    """ PIndex: Request a specified index from an array.
        """
    def __init__(self, index, list):
        self.index = index
        self.list = list

    def __next__(self):
        index = Pattern.value(self.index)
        list = Pattern.value(self.list)

        #------------------------------------------------------------------
        # null indices denote a rest -- so return a null value.
        # (same behaviour as PDegree: a degree of None returns a rest.)
        #------------------------------------------------------------------
        if index is None:
            return None
        else:
            index = int(index)
            return list[index]

class PKey(Pattern):
    """ PKey: Request a specified key from a dictionary.
        """
    def __init__(self, key, dict):
        self.key = key
        self.dict = dict

    def __next__(self):
        vkey = Pattern.value(self.key)
        vdict = Pattern.value(self.dict)
        return vdict[vkey]

class PConcat(Pattern):
    """ PConcat: Concatenate the output of multiple sequences. 

        >>> PConcat([ PSeq([ 1, 2, 3 ], 2), PSeq([ 9, 8, 7 ], 2) ]).nextn(16)
        [1, 2, 3, 1, 2, 3, 9, 8, 7, 9, 8, 7]
        """

    def __init__(self, inputs):
        self.inputs = inputs
        self.current = self.inputs.pop(0)

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
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a + b
        

class PSub(PBinOp):
    """ PSub: Subtract elements of two patterns (shorthand: patternA - patternB) """
    def __str__(self):
        return "%s - %s" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a - b

class PMul(PBinOp):
    """ PMul: Multiply elements of two patterns (shorthand: patternA * patternB) """
    def __str__(self):
        return "(%s) * (%s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a * b

class PDiv(PBinOp):
    """ PDiv: Divide elements of two patterns (shorthand: patternA / patternB) """
    def __str__(self):
        return "(%s) / (%s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a / b

class PFloorDiv(PBinOp):
    """ PFloorDiv: Integer division (shorthand: patternA // patternB) """
    def __str__(self):
        return "(%s) // (%s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a // b

class PMod(PBinOp):
    """ PMod: Modulo elements of two patterns (shorthand: patternA % patternB) """
    def __str__(self):
        return "(%s) %% (%s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a % b

class PPow(PBinOp):
    """ PPow: One pattern to the power of another (shorthand: patternA ** patternB) """
    def __str__(self):
        return "pow(%s, %s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else pow(a, b)

class PLShift(PBinOp):
    """ PLShift: Binary left-shift (shorthand: patternA << patternB) """
    def __str__(self):
        return "(%s << %s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a << b

class PRShift(PBinOp):
    """ PRShift: Binary right-shift (shorthand: patternA << patternB) """
    def __str__(self):
        return "(%s >> %s)" % (self.a, self.b)

    def __next__(self):
        a = next(self.a)
        b = next(self.b)
        return None if a is None or b is None else a >> b
