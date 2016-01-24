from collections import MappingView,KeysView,ValuesView,ItemsView
from networkx.exception import NetworkXError

class BaseEdgeView(MappingView):
    __slots__ = ('_adj','_node')
    def __init__(self, node, adj):
        self._adj = adj
        self._node = node
    def __iter__(self):
        seen = set()
        nodes_nbrs = self._adj.items()
        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                if nbr not in seen:
                    yield (n, nbr)
                    seen.add(n)
        del seen
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._adj.items()) // 2
    def __contains__(self, key):
        u,v = key
        return v in self._adj[u]
    def __getitem__(self, key):
        try:
            u,v = key
            return self._adj[u][v]
        except TypeError:
            raise NetworkXError('bad edge key: use edge key = (u,v)')
    def __and__(self, other):
        return set(self) & set(other)
    def __or__(self, other):
        return set(self) | set(other)
    def __xor__(self, other):
        return set(self) ^ set(other)
    def __sub__(self, other):
        return set(self) - set(other)
    def __repr__(self):
        return '{}'.format(list(self))

class Edges(BaseEdgeView):
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
    def keys(self):
        return EdgeKeys(self._adj)
    def data(self):
        return EdgeData(self._adj)
    def items(self):
        return EdgeItems(self._adj)
    def selfloops(self):
        return ((n, n)
                for n, nbrs in self._adj.items() if n in nbrs)

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



class EdgeKeys(BaseEdgeView):
    def __init__(self, adj):
        self._adj = adj


class EdgeData(BaseEdgeView):
    def __init__(self, adj):
        self._adj = adj
    def __iter__(self):
        seen = set()
        nodes_nbrs = self._adj.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                if nbr not in seen:
                    yield ddict
                    seen.add(n)
        del seen
    def __contains__(self, key):
        # need to look at all data
        for k in self:
            if k == key:
                return True
        return False

class EdgeItems(BaseEdgeView):
    def __init__(self, adj):
        self._adj = adj
    def __iter__(self):
        seen = set()
        nodes_nbrs = self._adj.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                if nbr not in seen:
                    yield (n,nbr),ddict
                    seen.add(n)
        del seen
    def __contains__(self, key):
        (u,v),d = key
        return v in self._adj[u] and self._adj[u][v] == d
