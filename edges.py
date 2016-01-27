from collections import MappingView, Set
from networkx.exception import NetworkXError


class BaseEdgeView(Set):
    __slots__ = ["_edgesobj"]
    def __init__(self, edgesobj):
        self._edgesobj = edgesobj
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
    def __len__(self):
        return len(self._edgesobj)
    # Set also demands __iter__ and __contains__ be defined. 

class EdgeKeys(BaseEdgeView):
    __slots__ = ["_edgesobj"]
    def __iter__(self):
        return iter(self._edgesobj)
    def __contains__(self, key):
        u,v = key
        return v in self._edgesobj._adj[u]

class EdgeData(BaseEdgeView):
    __slots__ = ["_edgesobj"]
    def __iter__(self):
        for e,d in self._edgesobj._items():
            yield d
    def __contains__(self, data):
        # Do we need/want to provide ability to look up a datadict?
        # need to look at all data
        for d in self:
            if d == data:
                return True
        return False

class EdgeItems(BaseEdgeView):
    __slots__ = ["_edgesobj"]
    def __iter__(self):
        return self._edgesobj._items()
    def __contains__(self, key):
        adj = self._edgesobj._adj
        (u,v),d = key
        return v in adj[u] and adj[u][v] == d


class UndirectedEdges(object):
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._adj.items()) // 2
    def __iter__(self):
        seen = set()
        nodes_nbrs = self._adj.items()
        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                if nbr not in seen:
                    yield (n, nbr)
                    seen.add(n)
        del seen
    def _items(self):
        seen = set()
        nodes_nbrs = self._adj.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                if nbr not in seen:
                    yield (n,nbr),ddict
                    seen.add(n)
        del seen
    def __contains__(self, key):
        u,v = key
        return v in self._adj[u]
    def __getitem__(self, key):
        try:
            u,v = key
            return self._adj[u][v]
        except TypeError:
            raise NetworkXError('bad edge key: use edge key = (u,v)')
    # Mutating Methods
    def add(self, u, v, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self._node:
            self._adj[u] = {} # fixme factory
            self._node[u] = {}
        if v not in self._node:
            self._adj[v] = {} # fixme factory
            self._node[v] = {}
        # add the edge
        datadict = self._adj[u].get(v, {}) # fixme factory
        datadict.update(attr_dict)
        self._adj[u][v] = datadict
        self._adj[v][u] = datadict
    def update(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
            elif ne == 2:
                u, v = e
                dd = {}  # doesnt need edge_attr_dict_factory
            else:
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,))
            if u not in self._node:
                self._adj[u] = {}
                self._node[u] = {}
            if v not in self._node:
                self._adj[v] = {}
                self._node[v] = {}
            datadict = self._adj[u].get(v, {})
            datadict.update(attr_dict)
            datadict.update(dd)
            self._adj[u][v] = datadict
            self._adj[v][u] = datadict
    def remove(self, u, v):
        try:
            del self._adj[u][v]
            if u != v:  # self-loop needs only one entry removed
                del self._adj[v][u]
        except KeyError:
            raise NetworkXError("The edge %s-%s is not in the graph" % (u, v))
    def clear(self):
        for n in self._adj:
            self._adj[n].clear()

class Edges(UndirectedEdges, Set):
    __slots__ = ('_adj','_node')
    def __init__(self, node, adj):
        self._adj = adj
        self._node = node
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
    def keys(self):
        return EdgeKeys(self)
    def data(self):
        return EdgeData(self)
    def items(self):
        return EdgeItems(self)
    def selfloops(self):
        return ((n, n)
                for n, nbrs in self._adj.items() if n in nbrs)
