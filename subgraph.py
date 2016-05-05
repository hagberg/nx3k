from collections import MappingView,KeysView,ValuesView,ItemsView

from nodes import Nodes
from edges import Edges
from adjacency import Adjacency


class Subgraph(object):
#    __slots__ = ('_nodedata','_adjacency','data')
    def __init__(self, graph, subnodes):
        # TODO Can we replace nbunch_iter with set(subnodes) & set(graph)?
        #      We lose the Error messages...
        self._subnodes = set(self._nbunch_iter(graph, subnodes))
        self._nodedata = SubNbrDict(self._subnodes, graph._nodedata)
        self._adjacency = SubAdjacency(self._subnodes, graph._adjacency)
        self.data = graph.data
        self.n = Nodes(self._nodedata, self._adjacency)
        self.e = Edges(self._nodedata, self._adjacency)
        self.a = self._adjacency
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._subnodes))
    def __iter__(self):
        return iter(self._subnodes)
    def __len__(self):
        return len(self._subnodes)

    @staticmethod
    def _nbunch_iter(graph, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(graph._adjacency)
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
            bunch = bunch_iter(nbunch, graph._adjacency)
        return bunch



class SubNbrDict(MappingView):
    # __slots__= ["_nodes","_mapping","_cache"]
    def __init__(self, nodes, mapping):
        # In nodes to be in subgraph, in mapping to be in nbrs.
        # So need intersection of nodes with mapping...
        self._nodes = set(nodes) & set(mapping)
        self._mapping = mapping
        self._cache = {}
    def __repr__(self):
        return '{0.__class__.__name__}({0._nodes}, {0._mapping})'.format(self)
    def __iter__(self):
        return iter(self._nodes)
    def __getitem__(self, n):
        if n in self._nodes:
            # Datadicts are read/write so no wrapper for mapping[n]
            return self._mapping[n]
        raise KeyError
    def __contains__(self, n):
        return n in self._nodes
    def __len__(self):
        return len(self._nodes)

    def keys(self):
        return self._nodes.keys()
    def data(self):
        # Datadicts are read/write so no wrapper for mapping[n]
        for n in self._nodes - set(self._cache.keys()):
            self._cache[n] = self._mapping[n]
        return self._cache.values()
    def items(self):
        # Datadicts are read/write so no wrapper for mapping[n]
        for n in self._nodes - set(self._cache.keys()):
            self._cache[n] = self._mapping[n]
        return self._cache.items()

class SubAdjacency(SubNbrDict):
    #__slots__ = ["_nodes","_mapping","_cache"]
    def __iter__(self):
        for n in self._nodes:
            if n in self._cache:
                yield (n, self._cache[n])
            else:
    # Edge-subgraph would need to check edges
    # perhaps with allowed_edges(u,v) function.
    # Then here we put:
    # allowed_n = [nbr for nbr in self._mapping[n]
    #              if nbr in self._nodes
    #              if allowed_edges(n,nbr)]
    # SubNbrDict(allowed_n, self._mapping[n])
                # NbrDicts are read-only so use wrapper for mapping[n]
                self._cache[n] = nd = SubNbrDict(self._nodes, self._mapping[n])
                yield (n, nd)
    def __getitem__(self, n):
        if n in self._cache:
            return self._cache[n]
        if n in self._nodes:
            # NbrDicts are read-only so use wrapper for mapping[n]
            self._cache[n] = nd = SubNbrDict(self._nodes, self._mapping[n])
            return nd
        raise KeyError
    def data(self):
        # NbrDicts are read-only so use wrapper for mapping[n]
        for n in self._nodes - set(self._cache.keys()):
            self._cache[n] = SubNbrDict(self._nodes, self._mapping[n])
        return self._cache.values() # Not readonly datadict
    def items(self):
        # NbrDicts are read-only so use wrapper for mapping[n]
        for n in self._nodes - set(self._cache.keys()):
            self._cache[n] = SubNbrDict(self._nodes, self._mapping[n])
        return self._cache.items()
