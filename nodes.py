from collections import Mapping, MutableMapping, Set
from networkx.exception import NetworkXError

class Nodes(MutableMapping, Set):
    __slots__ = ('_nodes', '_succ', '_pred')
    @classmethod
    def _from_iterable(self, it):
        return set(it)   # result of set operations is a builtin set

    def __init__(self, nodes, succ, pred):
        self._nodes = nodes
        self._succ = succ
        self._pred = pred
    # both set and dict methods
    def __getitem__(self, key):
        return self._nodes[key]
    def __iter__(self):
        return iter(self._nodes)
    def __len__(self):
        return len(self._nodes)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,self._nodes)
    # ABC classes provide the rest of nonmutating methods
    def __contains__(self, key):
        return key in self._nodes
    data = MutableMapping.values

    # Mutable methods
    def __delitem__(self, key):
        self.remove(key)
    def __setitem__(self, key, value):
#        self.add(key, value)  # probably a bad idea
        raise NetworkXError('Use the add() method')
    def add(self, n, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                msg = "The attr_dict argument must be a dictionary."
                raise NetworkXError(msg)
        if n not in self._nodes:
            self._succ[n] = {} # FIXME factory
            self._pred[n] = {} # FIXME factory
            self._nodes[n] = attr_dict
            return True # new node
        else:  # update attr even if node already exists
            self._nodes[n].update(attr_dict)
            return False # not new node
    def discard(self, n):
        try:
            # list handles self-loops (allow mutation later)
            nbrs = list(self._succ[n])
            del self._nodes[n]
        except KeyError: # silently ignore if node not present
            return
        for u in nbrs:
            del self._pred[u][n] # remove all edges n-u in digraph
        del self._succ[n]          # remove node from succ
        for u in self._pred[n]:
            del self._succ[u][n] # remove all edges n-u in digraph
        del self._pred[n]          # remove node from pred
    def remove(self, n):
        try:
            # list handles self-loops (allow mutation later)
            nbrs = list(self._succ[n])
            del self._nodes[n]
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError("The node %s is not in the graph."%(n,))
        for u in nbrs:
            del self._pred[u][n] # remove all edges n-u in digraph
        del self._succ[n]          # remove node from succ
        for u in self._pred[n]:
            del self._succ[u][n] # remove all edges n-u in digraph
        del self._pred[n]          # remove node from pred
    # inplace mass adds and removes
    def clear(self):
        self._nodes.clear()
        self._succ.clear()
        self._pred.clear()
    def update(self, nodes, **attr):
        for n in nodes:
            try:
                nn, ndict = n
                newdict = attr.copy()
                newdict.update(ndict)
                self.add(nn, **newdict)
            except TypeError:
                self.add(n, attr_dict=None, **attr)
        return self


    # this could be a view Degree(_nodes, _succ, _pred)
    def degree(self, weight=None):
        # yield tuple (n,degree)
        nodes_nbrs = ((n, succs, self._pred[n])
                      for n,succs in self._succ.items())
        if weight is None:
            for n, succ, pred in nodes_nbrs:
                yield (n, len(succ) + len(pred))
        else:
            for n, succ, pred in nodes_nbrs:
                degree = sum(data.get(weight,1) for data in succ.values()) +\
                         sum(data.get(weight,1) for data in pred.values())
                yield (n, degree)

    def selfloops(self):
        return (n for n, nbrs in self._succ.items() if n in nbrs)

class Degree(Mapping):
    __slots__ = ['_nodes', '_succ', '_pred']
    def __init__(self, nodes, succ, pred):
        self._nodes = nodes
        self._succ = succ
        self._pred = pred
    def __getitem__(self, node):
        return len(self._succ[node]) + len(self._pred[node])
    def __iter__(self):
        return iter(self._nodes)
    def __len__(self):
        return len(self._nodes)
    def weighted_items(self, weight='weight'):
        return DegreeItemsView(weight, self)

# shoud be from object -- no set methods needed.
class DegreeItemsView(Set):
    __slots__ = ['_weight', '_degree']
    def __init__(self, weight, degree):
        self._weight = weight
        self._degree = degree
    def __iter__(self):
        succ = self._degree._succ
        weight = self._weight
        try:
            pred = self._degree._pred
        except AttributeError:
            # only use _succ dict
            for n in self._degree._nodes:
                yield n, sum(data.get(weight,1) for data in succ.values())
        else:
            for n in self._degree._nodes:
                yield n, sum(data.get(weight,1) for data in succ.values()) +\
                         sum(data.get(weight,1) for data in pred.values())
    def __len__(self):
        return len(self._degree)
    def __contains__(self, item):
        (n, deg) = item
        succ = self._degree._succ
        if n not in succ:
            return False
        weight = self._weight
        try:
            pred = self._degree._pred
        except AttributeError:
            return sum(data.get(weight,1) for data in succ[n])
        else:
            return sum(data.get(weight,1) for data in succ[n]) +\
                   sum(data.get(weight,1) for data in pred[n])
        return n in self._degree and deg == self._degree[n]


class OutDegree(Degree):
    __slots__ = ['_graph', '_nodes', '_succ']
    def __init__(self, graph):
        self._graph = graph
        self._nodes = graph._nodes
        self._succ = graph._succ
    def __getitem__(self, node):
        return len(self._succ[node])

class InDegree(OutDegree):
    """Same as OutDegree, just call it with graph._pred instead of _succ"""
    pass
