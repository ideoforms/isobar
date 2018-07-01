from isobar.pattern import *
from isobar.util import *

import os
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
        elif nodes:
            raise ValueError("Invalid value for nodes")
        else:
            self.nodes = {}

        self.node = None

    def randomize(self):
        """ Uses the existing set of nodes but randomizes their connections. """
        for node in list(self.nodes.keys()):
            self.nodes[node] = []
            for other in list(self.nodes.keys()):
                prob = random.randint(0, 10)
                self.nodes[node] += [ other ] * prob

    def __next__(self):
        #------------------------------------------------------------------------
        # Returns the next value according to our internal statistical model.
        #------------------------------------------------------------------------
        if self.node is None and len(self.nodes) > 0:
            self.node = random.choice(list(self.nodes.keys()))
        else:
            try:
                #------------------------------------------------------------------------
                # 
                #------------------------------------------------------------------------
                self.node = random.choice(self.nodes[self.node])
            except IndexError:
                self.node = random.choice(list(self.nodes.keys()))
            except KeyError:
                print("no such node: %s" % self.node)

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

    def learn_pattern(self, pattern):
        """ Learns the sequence described in this pattern. """
        for value in pattern:
            self.register(value)

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
        return [learner.markov for learner in self.learners]

class MarkovGrapher:
    """ Helper class to graph the structure of a Markov object.
    Requires graphviz (pip install graphviz). """

    def __init__(self):
        self.pen_width_max = 3.0

    def render(self, markov, filename = "markov.pdf", name_map = None):
        """ Graphs the network described by 'markov'.
        If name_map is specified, apply this function to each node value
        to obtain its name.

        To graph a chain with integer node values mapped onto their 
        pitch names:

            MarkovGrapher.graph(markov, name_map = miditopitch)
        """
        from graphviz import Digraph

        graph = Digraph()
        items = []

        #------------------------------------------------------------------------
        # first pass: add nodes
        #------------------------------------------------------------------------
        if name_map:
            _name_map = lambda value: str(name_map(value))
        else:
            _name_map = str

        for index, node_value in enumerate(markov.nodes):
            graph.node(_name_map(node_value))

        #------------------------------------------------------------------------
        # second pass: add edges
        #------------------------------------------------------------------------
        for index, node_value in enumerate(markov.nodes):
            #------------------------------------------------------------------------
            # calculate a dictionary of normalised edge counts, such that an
            # isolated outgoing edge will always have a weight of 1.0, and a pair
            # of equally-weighted outgoing edges will have weights of 0.5 each.
            #------------------------------------------------------------------------
            edges = markov.nodes[node_value]
            edge_counts = dict((v, edges.count(v) / float(len(edges))) for v in edges)

            for edge, edge_weight in list(edge_counts.items()):
                #------------------------------------------------------------------------
                # in graphviz, attributes must always be strings.
                #------------------------------------------------------------------------
                pen_width = self.pen_width_max * edge_weight
                graph.edge(_name_map(node_value), _name_map(edge), penwidth = str(pen_width))

        #------------------------------------------------------------------------
        # render the graph using graphviz, deleting the intermediary source
        # file.
        #------------------------------------------------------------------------
        prefix, suffix = os.path.splitext(filename)
        graph.render(prefix, cleanup = True)

