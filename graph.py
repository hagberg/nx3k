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
        # graph = Graph((v,e)) where v is Graph.v like and e is Graph.e like
        # graph = Graph(({},e)) for an edgelist with no specified nodes
        # others with classmethods like
        # Graph.from_adjacency_matrix(m)
        # Graph.from_adjacency_list(l)
        #
        # should abstract the data here
        self._nodedata = {}  # empty node attribute dict
        self._adjacency = {}  # empty adjacency dict
        # the interface is n,e,a,data
        self.n = Nodes(self._nodedata, self._adjacency) # rename to self.nodes
        self.e = Edges(self._nodedata, self._adjacency) # rename to self.edges
        self.a = Adjacency(self._adjacency) # rename to self.adjacency
        self.data = {}   # dictionary for graph attributes
        # load with data
        if hasattr(data,'n') and not hasattr(data,'name'): # it is a new graph
            self.n.update(data.n)
            self.e.update(data.e)
            self.data.update(data.data)
            data = None
        try:
            nodes,edges = data # containers of edges and nodes
            self.n.update(nodes)
            self.e.update(edges)
        except: # old style
            if data is not None:
                convert.to_networkx_graph(data, create_using=self)
        # load __init__ graph attribute keywords
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
        s = sum(d for v, d in self.n.degree(weight=weight))
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2

    @classmethod
    def from_adjacency_matrix(self, matrix):
        import numpy as np
        kind_to_python_type={'f':float,
                             'i':int,
                             'u':int,
                             'b':bool,
                             'c':complex,
                             'S':str,
                             'V':'void'}
        try: # Python 3.x
            blurb = chr(1245) # just to trigger the exception
            kind_to_python_type['U']=str
        except ValueError: # Python 2.6+
            kind_to_python_type['U']=unicode
        n,m=matrix.shape
        if n!=m:
            raise nx.NetworkXError("Adjacency matrix is not square.",
                               "nx,ny=%s"%(matrix.shape,))
        dt=matrix.dtype
        try:
            python_type=kind_to_python_type[dt.kind]
        except:
            raise TypeError("Unknown numpy data type: %s"%dt)

        # Make sure we get even the isolated nodes of the graph.
        nodes = range(n)
        # Get a list of all the entries in the matrix with nonzero entries. These
        # coordinates will become the edges in the graph.
        edges = zip(*(np.asarray(matrix).nonzero()))
        # handle numpy constructed data type
        if python_type is 'void':
        # Sort the fields by their offset, then by dtype, then by name.
            fields = sorted((offset, dtype, name) for name, (dtype, offset) in
                            matrix.dtype.fields.items())
            triples = ((u, v, {name: kind_to_python_type[dtype.kind](val)
                               for (_, dtype, name), val in zip(fields, matrix[u, v])})
                       for u, v in edges)
        else:  # basic data type
            triples = ((u, v, dict(weight=python_type(matrix[u, v])))
                       for u, v in edges)
        graph = self((nodes, triples))
        return graph

    @classmethod
    def from_adjacency_list(self, adjlist):
        nodes = range(len(adjlist))
        edges = [(node,n) for node,nbrlist in enumerate(adjlist) for n in nbrlist]
        return self((nodes,edges))


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
