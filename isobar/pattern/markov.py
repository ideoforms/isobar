from isobar.pattern import *
from isobar.util import *

class PMarkov(Pattern):
	""" First-order Markov chain.
	http://pastebin.com/rNu2CSFs
	TODO: Implement n-order. """

	def __init__(self, nodes = None):
		#------------------------------------------------------------------------
		# avoid using [] (mutable default arguments considered harmful)
		# http://stackoverflow.com/questions/1132941/least-astonishment-in-python-the-mutable-default-argument
		#------------------------------------------------------------------------
		if isinstance(nodes, list):
			#------------------------------------------------------------------------
			# Learn a sequence of values by inferring probabilities
			#------------------------------------------------------------------------
			learner = MarkovLearner()
			for value in nodes:
				learner.register(value)
			self.nodes = learner.markov.nodes
		elif isinstance(nodes, dict):
			#------------------------------------------------------------------------
			# Take a dictionary argument with the same format as our internal nodes
			# model : eg { 1 : [ 2, 3 ], 2 : [ 3 ], 3 : [ 1, 2 ] }
			#------------------------------------------------------------------------
			self.nodes = nodes
		else:
			self.nodes = {}

		self.node = None

	def randomize(self):
		""" Uses the existing set of nodes but randomizes their connections. """
		for node in self.nodes.keys():
			self.nodes[node] = []
			for other in self.nodes.keys():
				prob = random.randint(0, 10)
				self.nodes[node] += [ other ] * prob

	def next(self):
		#------------------------------------------------------------------------
		# Returns the next value according to our internal statistical model.
		#------------------------------------------------------------------------
		if self.node is None and len(self.nodes) > 0:
			self.node = random.choice(self.nodes.keys())
		else:
			try:
				#------------------------------------------------------------------------
				# 
				#------------------------------------------------------------------------
				self.node = random.choice(self.nodes[self.node])
			except IndexError:
				self.node = random.choice(self.nodes.keys())
			except KeyError:
				print "no such node: %s" % self.node

		if self.node is None:
			print "PMarkov: got no next node :-("

		return self.node

	@classmethod
	def fromsequence(self, sequence):
		learner = MarkovLearner()
		for value in sequence:
			learner.register(value)
		return PMarkov(learner.markov)

	@classmethod
	def fromscale(self, scale):
		# TODO: BROKEN
		semitones = scale.semitones
		weights = scale.weights
		return PMarkov(semitones, [ weights[:] for _ in semitones ])

class MarkovLearner:
	def __init__(self):
		self.markov = PMarkov()
		self.last = None

	def register(self, value):
		# print "registering %s in %s (%s)" % (value, self.markov, self.markov.nodes)
		if value not in self.markov.nodes:
			self.markov.nodes[value] = []
		if self.last is not None:
			self.markov.nodes[self.last].append(value)
		self.last = value

class MarkovLParallel:
	def __init__(self, count):
		self.count = count
		self.learners = map(lambda n: MarkovLearner(), range(count))

	def register(self, list):
		for n in range(self.count):
			print "registering %d in %s" % (list[n], self.learners[n])
			self.learners[n].register(list[n])

	def normalize(self):
		for learner in self.learners:
			learner.markov.normalize()

	def chains(self):
		self.normalize()
		return map(lambda learner: learner.markov, self.learners)

