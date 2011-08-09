from isobar.note import *
from isobar.pattern import *

class LSystem:
	def __init__(self, rule = "N[-N++N]-N", seed = "N"):
		self.rule = rule
		self.seed = seed
		self.string = seed

		self.reset()

	def iterate(self, count = 3):
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
				# midinote = self.scale[self.state.degree]
				return Note(self.state.degree, self.state.velocity)
			elif token == '_':
				return Note.rest
			elif token == '-':
				self.state.degree = self.state.degree - 1
			elif token == '+':
				self.state.degree = self.state.degree + 1
			elif token == '\\':
				self.state.semitones = self.state.semitones - 1
			elif token == '/':
				self.state.semitones = self.state.semitones + 1
			elif token == '[':
				self.stack.append(self.state.copy())
				# print "pushing state: %s (new size = %d)" % (self.state, len(self.stack))
			elif token == ']':
				self.state = self.stack.pop()
				# print "popping state: %s (new size = %d)" % (self.state, len(self.stack))

		return None

	def reset(self):
		self.pos = 0
		self.stack = []
		self.state = LSysState()

class LSysState:
	def __init__(self, degree = 0, velocity = 64, semitones = 0):
		self.degree = degree
		self.velocity = velocity
		self.semitones = semitones

	def __str__(self):
		return "(%s, %s, %s)" % (self.degree, self.velocity, self.semitones)

	def copy(self):
		return LSysState(self.degree, self.velocity, self.semitones)

class PLSys(Pattern):
	"""Pattern: L-system"""

	def __init__(self, rule, depth = 3):
		self.rule = rule
		self.depth = depth
		self.reset()

	def __str__(self):
		return "lsystem (%s)" % rule

	def reset(self):
		self.lsys = LSystem(self.rule, "N")
		self.lsys.iterate(self.depth)

	def next(self):
		n = self.lsys.next()
		if n is None:
			self.lsys.reset()
			n = self.lsys.next()

		return None if n is None else n.midinote

