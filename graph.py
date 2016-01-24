from __future__ import division
from copy import deepcopy
import networkx as nx

from nodes import Nodes
from edges import Edges
from adjacency import Adjacency
from subgraph import Subgraph
import convert

class Graph(object):
    def __init__(self, data=None, **attr):
        # the init could be
        # graph = Graph(g) where g is a Graph
        # graph = Graph(e) where e is a Graph.e like
        # graph = Graph(v,e) where v is Graph.v like and e is Graph.e like
        # the rest of possible inits for data could be handled
        # with classmethods like
        # Graph.from_dict_of_dicts(dod)
        # Graph.from_list_of_lists(lol)
        # etc
        # should abstract the data here
        self._nodedata = {}  # empty node attribute dict
        self._adjacency = {}  # empty adjacency dict
        self.data = {}   # dictionary for graph attributes
        self.n = Nodes(self._nodedata, self._adjacency)
        self.e = Edges(self._nodedata, self._adjacency)
        self.a = Adjacency(self._adjacency)
        # attempt to load graph with data
        # would be nice to be able to do H = Graph(graph.n, graph.e)
        if data is not None:
            convert.to_networkx_graph(data, create_using=self)
        # load graph attributes (must be after convert)
        self.data.update(attr)


    def s(self, nbunch):
        H = Subgraph(self, nbunch)
        return H

    # crazy use of call - get subgraph?
    def __call__(self, nbunch):
        return self.s(nbunch)

    # rewrite these in terms of new interface
    def __iter__(self):
        return iter(self.n)

    def __len__(self):
        return len(self.n)

    def clear(self):
        self.name = ''
        self.n.clear()
        self.e.clear()
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

    def order(self):
        return len(self.n)

    def size(self, weight=None):
        s = sum(d for v, d in self.degree(weight=weight))
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2


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
    graph2 = Graph()
    graph2.e.add(0,1)
    graph2.e.add(1,2,foo='f',bar='b' )
    graph2.e.add(2,3)
    graph2.e.add(3,4)
    print(graph.n & graph2.n)

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

    print("----")

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
