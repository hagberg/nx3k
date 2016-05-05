from __future__ import division
from collections import Mapping
from copy import deepcopy
import networkx as nx

from nodes import Nodes
from edges import Edges
from adjacency import Adjacency, Successors, Predecessors
import convert as convert

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
        self._nodes = nd = {}  # empty node attribute dict
        self._succ = succ = {}  # empty adjacency dict
        self._pred = pred = {}  # empty adjacency dict
        self.directed = attr.pop("directed", False)
        # the interface is n,e,a,data
        self.n = Nodes(nd, succ, pred) # rename to self.nodes
        self.e = Edges(nd, succ, pred, self.directed) # rename to self.edges
        self.a = Adjacency(succ, pred) # rename to self.adjacency(adj?)
        self.su = Successors(succ) # rename to self.successors(succ?)
        self.pr = Predecessors(pred) # rename to self.predecessors(pred?)
        self.data = {}   # dictionary for graph attributes
        # load with data
        if hasattr(data,'n') and not hasattr(data,'name'): # it is a new graph
            self.n.update(data.n.items())
            self.e.update(data.e.items())
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
        return Subgraph(self, nbunch)

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
        G = self.__class__(self.s(self))
        #G.n.update(self.n)
        #G.e.update(self.e)
        return G

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return self.directed

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


class Subgraph(Graph):
    def __init__(self, graph, subnodes):
        # TODO Can we replace nbunch_iter with set(subnodes) & set(graph)?
        #      We lose the Error messages...
        self._subnodes = set(self._nbunch_iter(graph, subnodes))
        self._nodes = nd = SubNodes(self._subnodes, graph._nodes)
        self._succ = succ = SubAdjacency(self._subnodes, graph._succ)
        self._pred = pred = SubAdjacency(self._subnodes, graph._pred)
        #
        self.directed = graph.directed
        self.data = graph.data
        self.n = Nodes(nd, succ, pred) # rename to self.nodes
        self.e = Edges(nd, succ, pred, self.directed) # rename to self.edges
        self.a = Adjacency(succ, pred) # rename to self.adjacency(adj?)
        self.su = Successors(succ) # rename to self.successors(succ?)
        self.pr = Predecessors(pred) # rename to self.predecessors(pred?)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._subnodes))

    @staticmethod
    def _nbunch_iter(graph, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(graph._succ)
        elif nbunch in graph:  # if nbunch is a single node
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
            bunch = bunch_iter(nbunch, graph._succ)
        return bunch

class SubNodes(Mapping):
    """A read-only version of Nodes with a restricting nodeset"""
    __slots__ = ['_subnodes', '_nodedata']
    def __init__(self, subnodes, nodedata):
        self._subnodes = set(subnodes) & set(nodedata)
        self._nodedata = nodedata
    def __getitem__(self, node):
        if node in self._subnodes:
            return self._nodedata[node]
        raise KeyError("Node not found in subgraph nodes.")
    def __iter__(self):
        return iter(self._subnodes)
    def __len__(self):
        return len(self._subnodes)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._subnodes))

# Edge-subgraph would need to check edges
# perhaps with allowed_edges(u,v) function.
# Then here we put:
# allowed_n = [nbr for nbr in self._mapping[n]
#              if nbr in self._nodes
#              if allowed_edges(n,nbr)]
# SubNbrDict(allowed_n, self._mapping[n])
class SubAdjacency(SubNodes):
    __slots__ = ['_subnodes', '_nodedata', '_cache']
    def __init__(self, subnodes, nodedata):
        self._subnodes = subnodes
        self._nodedata = nodedata
        self._cache = {}
    def __getitem__(self, n):
        if n in self._cache:
            return self._cache[n]
        if n in self._subnodes:
            # NbrDicts are read-only so use wrapper for mapping[n]
            self._cache[n] = nd = SubNodes(self._subnodes, self._nodedata[n])
            return nd
        raise KeyError
#    def __iter__(self):
#        for n in self._subnodes:
#            if n in self._cache:
#                yield (n, self._cache[n])
#            else:
#                self._cache[n] = nd = SubNodes(self._subnodes, self._nodedata[n])
#                yield (n, nd)
    def values(self):
        # NbrDicts are read-only so use wrapper for mapping[n]
        for n in self._subnodes - set(self._cache.keys()):
            self._cache[n] = SubNodes(self._subnodes, self._nodedata[n])
        return self._cache.values() # Not readonly datadict
    def items(self):
        # NbrDicts are read-only so use wrapper for mapping[n]
        for n in self._subnodes - set(self._cache.keys()):
            self._cache[n] = SubNodes(self._subnodes, self._nodedata[n])
        return self._cache.items()


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

    print("-- subgraph --")

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
