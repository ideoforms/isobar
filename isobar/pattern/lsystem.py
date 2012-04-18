import random

from isobar.note import *
from isobar.pattern import *

class LSystem:
	def __init__(self, rule = "N[-N++N]-N", seed = "N"):
		self.rule = rule
		self.seed = seed
		self.string = seed

		self.reset()

	def iterate(self, count = 3):
		if self.rule.count("[") != self.rule.count("]"):
			raise ValueError, "Imbalanced brackets in rule string: %s" % self.rule

		for n in range(count):
			string_new = ""
			for char in self.string:
				string_new = string_new + self.rule if char == "N" else string_new + char

			self.string = string_new
			# print "(iter %d) string now %s" % (n, self.string)

	def next(self):
		while self.pos < len(self.string):
			token = self.string[self.pos]
			self.pos = self.pos + 1

			if token == 'N':
				return self.state
			elif token == '_':
				return None
			elif token == '-':
				self.state -= 1
			elif token == '+':
				self.state += 1
			elif token == '?':
				self.state += random.choice([ -1, 1 ])
			elif token == '[':
				self.stack.append(self.state)
			elif token == ']':
				self.state = self.stack.pop()

		raise StopIteration

	def reset(self):
		self.pos = 0
		self.stack = []
		self.state = 0


class PLSys(Pattern):
	"""Pattern: L-system"""

	def __init__(self, rule, depth = 3, loop = True):
		self.rule = rule
		self.depth = depth
		self.loop = loop
		self.reset()

	def __str__(self):
		return "lsystem (%s)" % rule

	def reset(self):
		self.lsys = LSystem(self.rule, "N")
		self.lsys.iterate(self.depth)

	def next(self):
		n = self.lsys.next()
		if self.loop and n is None:
			self.lsys.reset()
			n = self.lsys.next()

		return None if n is None else n

