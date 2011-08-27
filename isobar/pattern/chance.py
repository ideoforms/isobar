import sys
import random
import itertools

from isobar.pattern.core import *
from isobar.util import *

class PChoice(Pattern):
	"""Pattern: Random selection from list
		- values: list to select from"""
	def __init__(self, values = []):
		self.values = values

	def next(self):
		return self.values[random.randint(0, len(self.values) - 1)]

class PWChoice(Pattern):
	"""Pattern: Weighted random selection from list
		- values: list to select from
		- weights: equal-sized list of weightings (not necessarily normalized)"""
	def __init__(self, values = [], weights = []):
		self.values = values
		self.weights = weights

	def next(self):
		return wchoice(self.values, self.weights)

class PWhite(Pattern):
	"""Pattern: White noise 
		- min: minimum value
		- max: maximum value
	   If values are given as floats, output values are also floats < max.
	   If values are ints, output values are ints <= max (as random.randint)"""
	def __init__(self, min = 0.0, max = 1.0, length = sys.maxint):
		self.min = min
		self.max = max
		self.length = length

	def next(self):
		min = self.value(self.min)
		max = self.value(self.max)

		if type(min) == float:
			return random.uniform(min, max)
		else:
			return random.randint(min, max)

class PShuffle(Pattern):
	"""Pattern: Shuffled list"""
	def __init__(self, values = [], repeats = sys.maxint):
		self.values = values
		self.repeats = repeats
		self.pos = 0
		self.rcount = 1

	def reset(self):
		self.pos = 0
		self.rcount = 0

		Pattern.reset(self)

	def next(self):
		values = self.value(self.values)
		repeats = self.value(self.repeats)

		if self.pos >= len(values):
			if self.rcount >= repeats:
				return None
			self.rcount += 1
			self.pos = 0

		rv = values[self.pos]
		self.pos += 1
		return rv

class PBrown(Pattern):
	"""Pattern: Brownian noise"""
	def __init__(self, value = 0, step = 0.1, min = -1, max = 1, repeats = True, length = sys.maxint):
		self.init = value
		self.value = value
		self.step = step
		self.min = min
		self.max = max
		self.length = length
		self.repeats = repeats
		self.pos = 0

	def reset(self):
		self.value = self.init
		self.pos = 0

		Pattern.reset(self)

	def next(self):
		# pull out modulatable values
		vstep = Pattern.value(self.step)
		vmin = Pattern.value(self.min)
		vmax = Pattern.value(self.max)
		vrepeats = Pattern.value(self.repeats)
		# XXX todo - force no repeats

		if self.pos >= self.length:
			raise StopIteration
		rv = self.value
		self.pos += 1
		if type(vmin) == float:
			self.value += random.uniform(-vstep, vstep)
		else:
			# select new offset without repeats
			steps = range(-vstep, vstep + 1)
			if not vrepeats:
				steps.remove(0)
			self.value += random.choice(steps)
		self.value = min(max(self.value, vmin), vmax)

		return rv


class PWalk(Pattern):
	"""Pattern: Random walk around list"""
	def __init__(self, values = [], min = 1, max = 1):
		self.values = values
		self.min = min
		self.max = max
		self.pos = 0

	def next(self):
		# pull out modulatable values
		vvalues = self.value(self.values)
		vmin = self.value(self.min)
		vmax = self.value(self.max)

		move = random.randint(vmin, vmax)
		move = 0 - move if random.uniform(0, 1) < 0.5 else move
		self.pos += move

		if self.pos < 0:
			self.pos += len(vvalues)
		elif self.pos >= len(vvalues):
			self.pos -= len(vvalues)

		return vvalues[self.pos]

class PSelfIndex(Pattern):
	def __init__(self, count = 6):
		self.pos = 0
		self.values = range(count)
		random.shuffle(self.values)
		print "init values: %s" % self.values

	def next(self):
		if self.pos >= len(self.values):
			# re-index values
			self.pos = 0
			self.reindex()

		rv = self.values[self.pos]
		self.pos += 1

		return rv

	def reindex(self):
		values_new = []
		for n in range(len(self.values)):
			values_new.append(self.values[self.values[n]])
		print "new ordering: %s" % values_new
		self.values = values_new

class PSkip(Pattern):
	def __init__(self, pattern, play, random = True):
		self.pattern = pattern
		self.play = play
		self.random = random
		self.pos = 0.0

	def next(self):
		play = self.value(self.play)
		if self.random:
			if random.uniform(0, 1) < self.play:
				return self.pattern.next()
		else:
			self.pos += play
			if self.pos >= 1:
				self.pos -= 1
				return self.pattern.next()
