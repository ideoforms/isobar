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
			# take a dictionary argument to set our nodes, edges model
			self.nodes = nodes
		else:
			self.nodes = {}

		self.node = None

	def randomize(self):
		""" Takes a list of nodes and randomises over them. """
		self.edges = []
		for a in range(len(self.nodes)):
			self.edges.append([])
			for b in range(len(self.nodes)):
				# prob = random.randint(0, 2) / 2
				prob = random.uniform(0, 1)
				self.edges[a].append(prob)

		self.sanitize()

		print "new edges: %s" % self.edges

	def sanitize(self):
		# TODO: FIX
		for n, edge in enumerate(self.edges):
			if sum(edge) == 0:
				a = range(len(self.edges))
				a.remove(n)
				target = random.choice(a)
				# print "sanitizing edge %d (%s) with link to %d" % (n, self.nodes[n], target)
				edge[target] = 1

	def next(self, min = None, max = None):
		if self.node is None and len(self.nodes) > 0:
			self.node = random.choice(self.nodes.keys())
		else:
			try:
				self.node = random.choice(self.nodes[self.node])
			except IndexError:
				self.node = random.choice(self.nodes.keys())

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

	def next(self, min = None, max = None):
		return self.markov.next(min, max)

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

