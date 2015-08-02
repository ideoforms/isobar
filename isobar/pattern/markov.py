from isobar.pattern import *
from isobar.util import *

import sys

class PMarkov(Pattern):
	""" PMarkov: First-order Markov chain generator.
	
	"""
	# TODO: Implement n-order.

	def __init__(self, nodes = None):
		""" Create a new Markov chain. 'nodes' can be either be:
		 * an ordered sequence of notes (which will be used to infer the
		   probabilities of transitioning between notes), or
		 * a dictionary of the form { 1 : [ 2, 2, 3 ], 2 : [ 3 ], 3 : [ 1, 2 ] },
		   where values determine the probability of transitioning from A to B
		   based on the number of occurrences of B in the list with key A.
		"""
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
			# model : eg { 1 : [ 2, 2, 3 ], 2 : [ 3 ], 3 : [ 1, 2 ] }
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
			#--------------------------------------------------------------------------------
			# No node found.
			# TODO: Handle rests properly (as None values).
			#--------------------------------------------------------------------------------
			pass

		return self.node

	@classmethod
	def from_sequence(self, sequence):
		learner = MarkovLearner()
		for value in sequence:
			learner.register(value)
		return PMarkov(learner.markov)

class MarkovLearner:
	""" Learn a Markovian sequence by sequentially registering new values
	and building up a dynamic node graph. """

	def __init__(self):
		self.markov = PMarkov()
		self.last = None
	
	def get_markov(self):
		""" Returns the PMarkov pattern generator produced by the learning
		process. """
		return self.markov

	def register(self, value):
		if value not in self.markov.nodes:
			self.markov.nodes[value] = []
		if self.last is not None:
			self.markov.nodes[self.last].append(value)
		self.last = value

class MarkovParallelLearners:
	def __init__(self, count):
		self.count = count
		self.learners = [ MarkovLearner() for _ in range(count) ]

	def register(self, list):
		for n in range(self.count):
			self.learners[n].register(list[n])

	def chains(self):
		return map(lambda learner: learner.markov, self.learners)

class MarkovGrapher:
	""" Helper class to graph the structure of a Markov object.
	Requires gven. """
	def graph(self, markov):
		from gvgen import GvGen

		gv = GvGen()
		items = []

		gv.styleAppend("edge", "fontname", "gotham")
		gv.styleAppend("edge", "fontcolor", "#999999")
		gv.styleAppend("edge", "color", "#999999")

		gv.styleAppend("node", "fontname", "gotham")
		gv.styleAppend("node", "fontname", "gotham")
		gv.styleAppend("node", "shape", "circle")

		# first pass: add nodes
		for n, node in enumerate(markov.nodes):
			if type(node) == int:
				node = miditopitch(node)
			item = gv.newItem(str(node))
			items.append(item)
			gv.styleApply("node", item)

		# second pass: add edges
		for n, node in enumerate(markov.nodes):
			edges = markov.edges[n]
			for e in filter(lambda e: edges[e] > 0, range(len(edges))):
				link = gv.newLink(items[n], items[e], "%.1f" % edges[e])
				gv.styleApply("edge", link)
				# gv.propertyAppend(link, "weight", edges[e])

		gv.dot(sys.stderr)
