from collections import MappingView,KeysView,ValuesView,ItemsView
from dinodes import DiNodes
from diedges import DiEdges
from adjacency import Adjacency


class DiSubgraph(object):
#    __slots__ = ('_nodedata','_succ','_pred','data')
    def __init__(self, graph, subnodes):
        self._subnodes = set(self._nbunch_iter(graph, subnodes))
        self.data = graph.data
        self._nodedata = SubNodeData(self._subnodes, graph._nodedata)
        self._succ = SubAdjacency(self._subnodes, graph._succ)
        self._pred = SubAdjacency(self._subnodes, graph._pred)
        self.n = DiNodes(self._nodedata, self._succ, self._pred)
        self.e = DiEdges(self._nodedata, self._succ, self._pred)
        self.a = Adjacency(self._succ)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._subnodes))
    @staticmethod
    def _nbunch_iter(graph, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(graph._nodedata)
        elif nbunch in graph:  # if nbunch is a single node
            bunch = iter([nbunch])
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist, nodes):
                try:
                    for n in nlist:
                        if n in nodes:
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
            bunch = bunch_iter(nbunch, graph._nodedata)
        return bunch



class SubNodeData(MappingView):
    def __init__(self, nodes, mapping):
        self._nodes = nodes
        self._mapping = mapping
    def __iter__(self):
        for n in self._nodes:
            yield n
    def __getitem__(self, key):
        if key in self._nodes:
            return self._mapping[key]
        else:
            raise KeyError
    def __contains__(self, key):
        return key in self._nodes
    def __repr__(self):
        return '{}'.format(self._nodes)
    def __len__(self):
        return len(self._nodes)
    def keys(self):
        return KeysView(self._nodes)
    def items(self):
        return dict((k,v) for (k,v) in self._mapping.items() if k in self._nodes
).items()

class SubAdjacency(SubNodeData):
    def __iter__(self):
        for n in self._nodes:
            yield (n, SubNodeData(self._nodes, self._mapping[n]).items())
    def __getitem__(self, key):
        if key in self._nodes:
            return SubNodeData(self._nodes, self._mapping[key])
        else:
            raise KeyError
    def __repr__(self):
       return '{}'.format(self.items())
    def items(self):
        for n in self._nodes:
            yield (n, dict(SubNodeData(self._nodes, self._mapping[n]).items()))
