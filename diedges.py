from collections import MappingView,KeysView,ValuesView,ItemsView
from networkx.exception import NetworkXError

class BaseDiEdgeView(MappingView):
    __slots__ = ('_pred','_succ','_node')
    def __init__(self, node, succ, pred):
        self._node = node
        self._succ = succ
        self._pred = pred
    def __iter__(self):
        nodes_nbrs = self._succ.items()
        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                yield (n, nbr)
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._succ.items())
    def __contains__(self, key):
        try:
            u,v = key
            return v in self._succ[u]
        except KeyError:
            return False
    def __getitem__(self, key):
        try:
            u,v = key
            return self._succ[u][v]
        except (TypeError, ValueError):
            raise NetworkXError('bad edge key: use edge key = (u,v) or {u,v}')
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

class DiEdges(BaseDiEdgeView):
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
    def keys(self):
        return DiEdgeKeys(self._succ, self._pred)
    def data(self):
        return DiEdgeData(self._succ, self._pred)
    def items(self):
        return DiEdgeItems(self._succ, self._pred)
    def selfloops(self):
        return ((n, n)
                for n, nbrs in self._succ.items() if n in nbrs)

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
            self._succ[u] = {} # fixme factory
            self._pred[u] = {} # fixme factory
            self._node[u] = {}
        if v not in self._node:
            self._succ[v] = {} # fixme factory
            self._pred[v] = {} # fixme factory
            self._node[v] = {}
        # add the edge
        datadict = self._succ[u].get(v, {}) # fixme factory
        datadict.update(attr_dict)
        self._succ[u][v] = datadict
        self._pred[v][u] = datadict


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
                self._node[u] = {}
                self._succ[u] = {}
                self._pred[u] = {}
            if v not in self._node:
                self._node[v] = {}
                self._succ[v] = {}
                self._pred[v] = {}
            datadict = self._succ[u].get(v, {})
            datadict.update(attr_dict)
            datadict.update(dd)
            self._succ[u][v] = datadict
            self._pred[v][u] = datadict

    def remove(self, u, v):
        try:
            del self._succ[u][v]
            del self._pred[v][u]
        except KeyError:
            msg = "The edge %s-%s is not in the graph" % (u, v)
            raise NetworkXError(msg)

    def clear(self):
        for n in self._succ:
            self._succ[n].clear()
            self._pred[n].clear()



class DiEdgeKeys(BaseDiEdgeView):
    def __init__(self, succ, pred):
        self._succ = succ
        self._pred = pred


class DiEdgeData(BaseDiEdgeView):  # out_edges... switch inputs for in_edges
    def __init__(self, succ, pred):
        self._succ = succ
        self._pred = pred
    def __iter__(self):
        nodes_nbrs = self._succ.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                yield ddict
    def __contains__(self, key):
        # need to look at all edges data dicts
        for ddict in self:
            if key in ddict:
                return True
        return False

class DiEdgeItems(BaseDiEdgeView):
    def __init__(self, succ, pred):
        self._succ = succ
        self._pred = pred
    def __iter__(self):
        nodes_nbrs = self._succ.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                yield (n,nbr),ddict
    def __contains__(self, key):
        try:
            (u,v),d = key
        except (TypeError, ValueError):
            msg = "Valid EdgeItems have form ((u,v),d): {}".format(key)
            raise NetworkXError(msg)
        try:
            return v in self._succ[u] and self._succ[u][v] == d
        except KeyError:
            return False

