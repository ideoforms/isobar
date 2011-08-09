from gvgen import *
from isobar.util import *
import sys

class Grapher:
    def graph(self, markov):
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
