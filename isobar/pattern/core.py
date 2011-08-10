import sys
import copy
import random
import itertools

class Pattern:
	LENGTH_MAX = 65536

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

	def __iter__(self):
		return self

	def next(self):
		return self.__generator__.next()

	def values(self):
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
		pass

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

