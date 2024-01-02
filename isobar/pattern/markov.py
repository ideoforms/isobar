from __future__ import annotations
from .chance import PStochasticPattern
from .core import Pattern

import os
from typing import Iterable

class PMarkov(PStochasticPattern):
    """ PMarkov: First-order Markov chain generator.
    """

    def __init__(self, nodes: Iterable = None):
        """ Create a new Markov chain. 'nodes' can be either be:
         * an ordered sequence of notes (which will be used to infer the
           probabilities of transitioning between notes), or
         * a dictionary of the form { 1 : [ 2, 2, 3 ], 2 : [ 3 ], 3 : [ 1, 2 ] },
           where values determine the probability of transitioning from A to B
           based on the number of occurrences of B in the list with key A.
        """
        super().__init__()

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

        self.reset()

    def __repr__(self):
        return ("PMarkov(%s)" % repr(nodes))

    def randomize(self):
        """ Uses the existing set of nodes but randomizes their connections. """
        for node in list(self.nodes.keys()):
            self.nodes[node] = []
            for other in list(self.nodes.keys()):
                prob = self.rng.randint(0, 10)
                self.nodes[node] += [other] * prob

    def reset(self):
        super().reset()
        self.node = None

    def __next__(self):
        if self.node is None and len(self.nodes) > 0:
            self.node = self.rng.choice(list(self.nodes.keys()))

        #------------------------------------------------------------------------
        # Returns the next value according to our internal statistical model.
        #------------------------------------------------------------------------
        if self.node not in self.nodes or len(self.nodes[self.node]) == 0:
            raise StopIteration

        try:
            self.node = self.rng.choice(self.nodes[self.node])
        except IndexError:
            raise StopIteration
        except KeyError:
            print("No such node: %s" % self.node)

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

    def __repr__(self):
        return ("MarkovLearner()")

    def learn_pattern(self, pattern: Pattern):
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
    def __init__(self, count: int):
        self.count = count
        self.learners = [MarkovLearner() for _ in range(count)]

    def __repr__(self):
        return ("MarkovParallelLearners(%s)" % self.count)

    def register(self, list: Iterable):
        for n in range(self.count):
            self.learners[n].register(list[n])

    def chains(self) -> list:
        return [learner.markov for learner in self.learners]

class MarkovGrapher:
    """ Helper class to graph the structure of a Markov object.
    Requires graphviz (pip install graphviz). """

    def __init__(self):
        self.pen_width_max = 3.0

    def __repr__(self):
        return "MarkovGrapher()"

    def render(self, markov, filename: str = "markov.pdf", name_map=None):
        """ Graphs the network described by 'markov'.
        If name_map is specified, apply this function to each node value
        to obtain its name.

        To graph a chain with integer node values mapped onto their
        pitch names:

            MarkovGrapher.graph(markov, name_map = miditopitch)
        """
        from graphviz import Digraph

        graph = Digraph()

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
                graph.edge(_name_map(node_value), _name_map(edge), penwidth=str(pen_width))

        #------------------------------------------------------------------------
        # render the graph using graphviz, deleting the intermediary source
        # file.
        #------------------------------------------------------------------------
        prefix, suffix = os.path.splitext(filename)
        graph.render(prefix, cleanup=True)
