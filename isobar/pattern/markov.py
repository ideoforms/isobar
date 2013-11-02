from isobar.pattern import *
from isobar.util import *

class Markov:
	""" First-order Markov chain.
	http://pastebin.com/rNu2CSFs
	TODO: Implement n-order. """

	def __init__(self, nodes = None):
		#------------------------------------------------------------------------
		# avoid using [] (mutable default arguments considered harmful)
		# http://stackoverflow.com/questions/1132941/least-astonishment-in-python-the-mutable-default-argument
		#------------------------------------------------------------------------
		if isinstance(nodes, list):
			# learn a sequence of values
			learner = MarkovLearner()
			for value in nodes:
				learner.register(value)
			self.nodes = learner.markov.nodes
		elif isinstance(nodes, dict):
			#------------------------------------------------------------------------
			# take a dictionary argument to initialise our nodes, edges model
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
		if self.node is None and len(self.nodes) > 0:
			self.node = random.choice(self.nodes.keys())
		else:
			try:
				self.node = random.choice(self.nodes[self.node])
			except IndexError:
				self.node = random.choice(self.nodes.keys())
			except KeyError:
				print "no such node: %s" % self.node

		if self.node is None:
			print "PMarkov: got no next node :-("

		return self.node

class PMarkov(Pattern):
	""" PMarkov: Markov chain """
	def __init__(self, param):
		""" can take either a Markov object, or a dict of nodes """
		if isinstance(param, Markov):
			self.markov = param
		else:
			self.markov = Markov(param)

	def next(self):
		return self.markov.next()

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
		self.markov = Markov()
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

