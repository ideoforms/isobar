from isobar.pattern import *
from isobar.util import *

class Markov:
	def __init__(self, nodes = [], edges = []):
		self.nodes = nodes
		self.edges = edges
		self.node = 0
		if len(self.nodes) > 0:
			self.node = random.randint(0, len(self.nodes) - 1)
		if len(self.edges) == 0:
			self.randomize()

	def randomize(self):
		self.edges = []
		for a in range(len(self.nodes)):
			self.edges.append([])
			for b in range(len(self.nodes)):
				# prob = random.randint(0, 2) / 2
				prob = random.uniform(0, 1)
				self.edges[a].append(prob)

		self.normalize()
		self.sanitize()

		print "new edges: %s" % self.edges
	def normalize(self):
		self.edges = map(lambda n: normalize(n), self.edges)

	def sanitize(self):
		for n, edge in enumerate(self.edges):
			if sum(edge) == 0:
				a = range(len(self.edges))
				a.remove(n)
				target = random.choice(a)
				# print "sanitizing edge %d (%s) with link to %d" % (n, self.nodes[n], target)
				edge[target] = 1

	def next(self, min = None, max = None):
		if min is not None:
			edges = self.edges[self.node][:]
			# print "selecting from some - %s" % edges
			for n, edge in enumerate(edges):
				if not min <= self.nodes[n] <= max:
					edges[n] = 0
			index = wnindex(edges)
		else:
			# print "selecting from all - %s" % self.edges[self.node]
			index = windex(self.edges[self.node])

		if index is not None:
			# print "moving from %d -> %d (prob %.2f)" % (self.node, index, self.edges[self.node][index])
			self.node = index
		return self.nodes[self.node]

class PMarkov(Pattern):
	""" PMarkov: Markov chain """
	def __init__(self, param, edges = []):
		""" can take either a Markov object, or [ nodes, edges ] pair """
		if isinstance(param, Markov):
			self.markov = param
		else:
			self.markov = Markov(param, edges)
		self.markov.normalize()

	def next(self, min = None, max = None):
		return self.markov.next(min, max)

class MarkovLearner:
	def __init__(self):
		# XXX! weeird bug - not passing an empty list here seems to share the same nodes ref between markov objects.
		# why?
		self.markov = Markov([])
		print "new learner, markov is %s" % self.markov
		self.last = None

	def register(self, value):
		# print "registering %s in %s (%s)" % (value, self.markov, self.markov.nodes)
		if value not in self.markov.nodes:
			self.markov.edges.append(map(lambda n: 0, range(len(self.markov.nodes))))
			self.markov.nodes.append(value)
			for edge in self.markov.edges:
				edge.append(0)
		if self.last is not None:
			i_last = self.markov.nodes.index(self.last)
			i_cur  = self.markov.nodes.index(value)
			self.markov.edges[i_last][i_cur] += 1
		self.last = value

		# print "markof nodes now %s, edges %s" % (self.markov.nodes, self.markov.edges)

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

