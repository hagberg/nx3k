from __future__ import division
from copy import deepcopy
import networkx as nx
from networkx.exception import NetworkXError
import networkx.convert as convert

from nodes import Nodes
from edges import Edges
from adjacency import Adjacency
from subgraph import Subgraph
import convert

class Graph(object):
    def __init__(self, data=None, **attr):
        self._nodedata = {}  # empty node attribute dict
        self._adjacency = {}  # empty adjacency dict
        self.n = Nodes(self._nodedata, self._adjacency)
        self.e = Edges(self._nodedata, self._adjacency)
        self.a = Adjacency(self._adjacency)
        self.data = {}   # dictionary for graph attributes
        # attempt to load graph with data
        # would be nice to be able to do H = Graph(graph.n, graph.e)
        if data is not None:
            convert.to_networkx_graph(data, create_using=self)
        # load graph attributes (must be after convert)
        self.data.update(attr)

    def s(self, nbunch):
        bunch = set(self._nbunch_iter(nbunch))
        H = Subgraph(self, bunch)
        return H

    # crazy use of call - get subgraph?
    def __call__(self, nbunch):
        return self.s(nbunch)


    # rewrite these in terms of new interface
    def __iter__(self):
        return iter(self.n)
    def __len__(self):
        return len(self.n)
    def number_of_nodes(self):
        return len(self.n)
    def order(self): # deprecate?
        return len(self.n)

    def clear(self):
        self.name = ''
        self._adjacency.clear()
        self._nodedata.clear()
        self.data.clear()

    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        G = self.__class__()
        G.n.update(self.n)
        G.e.update(self.e)
        return G

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return False

    def to_directed(self):
        from networkx import DiGraph
        G = DiGraph()
        G.name = self.name
        G.add_nodes_from(self.n)
        G.add_edges_from(((u, v, deepcopy(data))
            for u, nbrs in self.a
            for v, data in nbrs.items()))
        G.graph = deepcopy(self.data)
        G._nodedata = deepcopy(self._nodedata)
        G.node = G._nodedata # hack to pass test
        return G

    def to_undirected(self):
        return deepcopy(self)

    def size(self, weight=None):
        s = sum(d for v, d in self.degree(weight=weight))
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2

    def number_of_edges(self, u=None, v=None):
        if u is None:
            return int(self.size())
        if v in self.a[u]:
            return 1
        else:
            return 0

    # not sure where this one goes - maybe to Subgraph
    def _nbunch_iter(self, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(self._adjacency)
        elif nbunch in self:  # if nbunch is a single node
            bunch = iter([nbunch])
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist, adj):
                try:
                    for n in nlist:
                        if n in adj:
                            yield n
                except TypeError as e:
                    message = e.args[0]
                    # capture error for non-sequence/iterator nbunch.
                    if 'iter' in message:
                        raise NetworkXError(
                            "nbunch is not a node or a sequence of nodes.")
                    # capture error for unhashable node.
                    elif 'hashable' in message:
                        raise NetworkXError(
                            "Node {} in the sequence nbunch is not a valid node.".format(n))
                    else:
                        raise
            bunch = bunch_iter(nbunch, self._adjacency)
        return bunch



if __name__ == '__main__':
    graph = Graph()
    graph.e.add(1,2,foo='f',bar='b' )
    graph.e.add(2,3,foo='f',bar='b' )
    graph.e.add(3,4,foo='f',bar='b' )
    graph.e.add(4,5)
    print(graph.n)
    print(graph.n.keys())
    print(graph.n.data())
    print(graph.n.items())
    print(len(graph.n))
    print(1 in graph.n)
#    graph2 = Graph()
#    graph2.add_path([1,2,3,4])
#    print(graph.n & graph2.n)
#    print(graph.n.items())

    print(graph.e)
    print(len(graph.e))
    print(graph.e.keys())
    print(graph.e.data())
    print(graph.e.items())
    print([(e,d.get('foo','default')) for (e,d) in graph.e.items()])
    print((2,3) in graph.e)
    print((2,3) in graph.e.keys())
#    print(graph.e & graph2.e)
    print(graph.e[(1,2)])

    print "----"

    graph.n[1]['a']='b'
    s = graph.s([1,2])
    print(s)
    print(s.n)
    print(s.n.items())
    print(s.e)
    print(s.e.keys())
    print(s.e.data())
    print(s.e.items())
    print(s.a)

    print(graph.s([1,2]).e.items())
    print([(e,d.get('foo','default')) for (e,d) in graph.s([1,2]).e.items()])
