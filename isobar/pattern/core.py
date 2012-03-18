#-------------------------------------------------------------------------------
# isobar: a python library for expressing and manipulating musical patterns.
#-------------------------------------------------------------------------------

import sys
import copy
import random
import itertools

import isobar


class Pattern:
	""" Pattern: Abstract superclass of all pattern generators.

		Patterns are at the core of isoar. A Pattern implements the iterator
		protocol, representing a sequence of values which are iteratively
		returned by the next() method. A pattern may be finite, after which
		point it raises an EndOfPattern exception. Call reset() to return
		a pattern to its initial state.

		Patterns can be subject to standard arithmetic operators as expected.
		"""

	LENGTH_MAX = 65536
	GENO_SEPARATOR = "/"

	def __init__(self):
		self.__generator__ = itertools.count(0)

	def __str__(self):
		return "pattern"

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

	def __div__(self, operand):
		"""Binary op: divide two patterns"""
		operand = Pattern.pattern(operand)
		return PDiv(self, operand)

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
				rv.append(self.next())
		except StopIteration:
			pass

		return rv

	def next(self):
		return self.__generator__.next()

	def all(self):
		values = []
		try:
			# do we even need a LENGTH_MAX?
			# if we omit it, .all() will become an alias for list(pattern)
			#  - maybe not such a bad thing.
			for n in xrange(Pattern.LENGTH_MAX):
				value = self.next()
				values.append(value)
		except StopIteration:
			pass

		self.reset()
		return values

	def reset(self):
		""" reset a finite sequence back to position 0 """
		fields = vars(self)
		for name, field in fields.items():
			if isinstance(field, Pattern):
				field.reset()

	@staticmethod
	def fromgenotype(genotype):
		""" create a new object based on this genotype """
		print "genotype: %s" % genotype
		parts = genotype.split(Pattern.GENO_SEPARATOR)
		classname = parts[0]
		arguments = parts[1:]
		try:
			classes = vars(isobar)
			classobj = classes[classname]
			instance = classobj()
			fields = vars(instance)
			counter = 0
			for name, field in fields.items():
				instance.__dict__[name] = eval(arguments[counter])
				print "%s - %s" % (name, arguments[counter])
				counter += 1
		except Exception, e:
			print "fail: %s" % e
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
		print "A %s\nB %s\n> %s" % (genotypeA, genotypeB, genotypeC)
		return Pattern.fromgenotype(genotypeC)

	def genotype(self):
		""" return a string representation of this pattern, suitable for breeding """
		genotype = "%s" % (self.__class__.__name__)
		fields = vars(self)

		import base64

		for name, field in fields.items():
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
		return Pattern.value(v.next()) if isinstance(v, Pattern) else v

	@staticmethod
	def pattern(v):
		""" Patternify a value by wrapping it in PConst if necessary. """
		return v if isinstance(v, Pattern) else PConst(v)

class PConst(Pattern):
	""" PConst: Constant pattern.
        Returns a fixed value.

		>>> p = PConst(4)
		>>> p.nextn(16)
		[4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
		"""
	def __init__(self, constant):
		self.constant = constant

	def __str__(self):
		return "constant"

	def next(self):
		return self.constant

class PRef(Pattern):
	""" PRef: Pattern reference.
	    Returns the next value of the pattern contained.
		Useful to change an inner pattern in real time.
		"""
	def __init__(self, pattern):
		self.pattern = pattern

	def change(self, pattern):
		self.pattern = pattern

	def next(self):
		return self.pattern.next()

class PDict(Pattern):
	""" PDict : A dict of patterns.
        Thanks to Dan Stowell <http://www.mcld.co.uk/>
	    """
	def __init__(self, dict = {}):
		self.dict = dict

	def next(self):
		vdict = self.value(self.dict)
		rv = dict((k, Pattern.value(vdict[k])) for k in vdict)

		return rv

class PFunc(Pattern):
	""" PFunc: Applies the given function to each event in its input.
	    """
	def __init__(self, fn, pattern):
		self.fn = fn
		self.pattern = Pattern.pattern(pattern)

	def next(self):
		value = self.pattern.next()
		return self.fn(value)

#------------------------------------------------------------------
# binary operators
#------------------------------------------------------------------

class PBinOp(Pattern):
	def __init__(self, a, b):
		self.a = a
		self.b = b

class PAdd(PBinOp):
	def __str__(self):
		return "%s + %s" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a + b
		

class PSub(PBinOp):
	def __str__(self):
		return "%s - %s" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a - b

class PMul(PBinOp):
	def __str__(self):
		return "(%s) * (%s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a * b

class PDiv(PBinOp):
	def __str__(self):
		return "(%s) / (%s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a / b

class PMod(PBinOp):
	def __str__(self):
		return "(%s) % (%s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a % b

class PPow(PBinOp):
	def __str__(self):
		return "pow(%s, %s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else pow(a, b)

class PLShift(PBinOp):
	def __str__(self):
		return "(%s << %s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a << b

class PRShift(PBinOp):
	def __str__(self):
		return "(%s >> %s)" % (self.a, self.b)

	def next(self):
		a = self.a.next()
		b = self.b.next()
		return None if a is None or b is None else a >> b
