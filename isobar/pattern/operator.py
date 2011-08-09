"""Testing pydoc"""

import sys
import random
import itertools

from isobar.pattern.core import *
from isobar.key import *
from isobar.util import *

class PDelay(Pattern):
	""" outputs the next value of patternA after patternB ticks """

	def __init__(self, source, delay):
		self.source = source
		self.delay = delay
		self.counter = self.value(self.delay)

	def next(self):
		self.counter -= 1
		if self.counter < 0:
			self.counter = self.value(self.delay)
			return self.value(self.source)

class PDiff(Pattern):
	""" outputs the difference between the current and previous values of an input pattern """

	def __init__(self, source):
		self.source = source
		self.current = self.value(self.source)

	def next(self):
		next = self.value(self.source)
		rv = next - self.current
		self.current = next
		return rv

class PAbs(Pattern):
	""" absolute values """

	def __init__(self, source):
		self.source = source

	def next(self):
		next = self.value(self.source)
		if next is not None:
			return abs(next)
		return next

