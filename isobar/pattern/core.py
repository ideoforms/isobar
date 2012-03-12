import sys
import copy
import random
import itertools

import isobar

class EndOfPattern(Exception):
	""" Exception signalling the end of an isobar pattern.
	    """
	pass

class Pattern:
	""" Pattern: Abstract superclass of all pattern generators.

		Patterns are at the core of isoar. A Pattern implements the iterator
		protocol
	"""

	LENGTH_MAX = 65536
	GENO_SEPARATOR = "/"

	def __init__(self):
		self.__generator__ = itertools.count(0)

	def __str__(self):
		return "pattern"

	def __neg__(self):
		return 0 - self

	def __add__(self, operand):
		"""Binary op: add two patterns"""
		# operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
		# return PAdd(copy.deepcopy(self), operand)

		# we actually want to retain references to our constituent patterns
		# in case the user later changes parameters of one
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PAdd(self, operand)

	def __radd__(self, operand):
		"""Binary op: add two patterns"""
		return self.__add__(operand)

	def __sub__(self, operand):
		"""Binary op: subtract two patterns"""
		# operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
		# return PSub(copy.deepcopy(self), operand)
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PSub(self, operand)

	def __rsub__(self, operand):
		"""Binary op: subtract two patterns"""
		# operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
		# return PSub(operand, copy.deepcopy(self))
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PSub(operand, self)

	def __mul__(self, operand):
		"""Binary op: multiply two patterns"""
		# operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
		# return pmul(copy.deepcopy(self), operand)
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PMul(self, operand)

	def __rmul__(self, operand):
		"""Binary op: multiply two patterns"""
		return self.__mul__(operand)

	def __div__(self, operand):
		"""Binary op: divide two patterns"""
		# operand = copy.deepcopy(operand) if isinstance(operand, pattern) else PConst(operand)
		# return PDiv(copy.deepcopy(self), operand)
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PDiv(self, operand)

	def __rdiv__(self, operand):
		"""Binary op: divide two patterns"""
		return self.__div__(operand)

	def __mod__(self, operand):
		"""Modulo"""
		operand = operand if isinstance(operand, Pattern) else PConst(operand)
		return PMod(self, operand)

	def __iter__(self):
		return self

	def nextn(self, count):
		return [ self.next() for n in range(count) ]

	def next(self):
		return self.__generator__.next()

	def all(self):
		values = []
		for n in xrange(Pattern.LENGTH_MAX):
			value = self.next()
			if value is None:
				break
			else:
				values.append(value)

		self.reset()
		return values

	def reset(self):
		""" reset a finite sequence back to position 0 """
		fields = vars(self)
		for name, field in fields.items():
			if isinstance(field, Pattern):
				# print "reset: %s" % name
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
		if isinstance(v, Pattern):
			return Pattern.value(v.next())
		else:
			return v

class PConst(Pattern):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "constant"

	def next(self):
		return self.value

class PDict(Pattern):
	""" Pattern: A dict of patterns.
        Thanks to Dan Stowell <http://www.mcld.co.uk/>
	    """
	def __init__(self, dict = {}):
		self.dict = dict

	def next(self):
		vdict = self.value(self.dict)
		rv = dict((k, Pattern.value(vdict[k])) for k in vdict)

		return rv

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
