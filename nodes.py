from collections import KeysView,ValuesView,ItemsView,MutableMapping
from networkx.exception import NetworkXError

class NodeKeys(KeysView):
    def __repr__(self):
        return '{}'.format(list(self._mapping))

class NodeData(ValuesView):
    def __repr__(self):
        return '{}'.format(list(self._mapping.values()))

class NodeItems(ItemsView):
    def __repr__(self):
        return '{}'.format(list(self._mapping.items()))

class Nodes(MutableMapping):
    __slots__ = ('_nodes','_adj')
    def __init__(self, nodes, adj=None):
        self._nodes = nodes
        self._adj = adj
    # both set and dict methods
    def __iter__(self):
        for n in self._nodes:
            yield n
    def __contains__(self, key):
        return key in self._nodes
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._nodes))
    def __len__(self):
        return len(self._nodes)
    def clear(self):
        self._nodes.clear()
        self._adj.clear()
    # set methods
    def __and__(self, other):
        return set(self._nodes) & set(other)
    def __or__(self, other):
        return set(self._nodes) | set(other)
    def __xor__(self, other):
        return set(self._nodes) ^ set(other)
    def __sub__(self, other):
        return set(self._nodes) - set(other)
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
    def intersection_update(self, nodes):
        # fixme: make work for node tuples?
        for n in self - nodes:
            self.discard(n)
        return self
    def symmetric_difference_update(self, nodes):
        # fixme: make work for node tuples?
        discard = self & nodes
        add = nodes - self
        for n in discard:
            self.discard(n)
        for n in add:
            self.add(n)
        return self
    def difference_update(self, nodes):
        # fixme: make work for node tuples?
        for n in nodes:
            self.discard(n)
        return self
    __ior__ = update # |=
    __iand__ = intersection_update # &=
    __isub__ = difference_update # -=
    __ixor__ = symmetric_difference_update # ^=


    def discard(self, n):
        adj = self._adj
        try:
            # keys handles self-loops (allow mutation later)
            nbrs = list(adj[n].keys())
            del self._nodes[n]
        except KeyError:  # NetworkXError if n not in self
            return
        for u in nbrs:
            del adj[u][n]   # remove all edges n-u in graph
        del adj[n]          # now remove node
    def remove(self, n):
        adj = self._adj
        try:
            # keys handles self-loops (allow mutation later)
            nbrs = list(adj[n].keys())
            del self._nodes[n]
        except KeyError:  # NetworkXError if n not in self
            raise NetworkXError("The node %s is not in the graph." % (n,))
        for u in nbrs:
            del adj[u][n]   # remove all edges n-u in graph
        del adj[n]          # now remove node


    # dictionary methods
    def __delitem__(self, key):
        self.remove(key)
    def __setitem__(self, key, value):
#        self.add(key, value)  # probably a bad idea
        raise NetworkXError('Use the add() method')
    def __getitem__(self, key):
        return self._nodes[key]
    def keys(self):
#        return self._nodes.keys()
        return NodeKeys(self._nodes)
    def items(self):
#        return self._nodes.items()
        return NodeItems(self._nodes)
    def values(self):
#        return self._nodes.values()
        return NodeData(self._nodes)


    def add(self, n, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        if n not in self._nodes:
            self._adj[n] = {} # FIXME factory
            self._nodes[n] = attr_dict
        else:  # update attr even if node already exists
            self._nodes[n].update(attr_dict)


    # extra methods: neither set or dict

    def data(self):
#        return self._nodes.values()
        return NodeData(self._nodes)

    # this could be a view
    def degree(self, weight=None):
        if weight is None:
            for n, nbrs in self._adj.items():
                # return tuple (n,degree)
                yield (n, len(nbrs) + (1 if n in nbrs else 0))
        else:
            for n, nbrs in self._adj.items():
                yield (n, sum((nbrs[nbr].get(weight, 1) for nbr in nbrs)) +
                       (nbrs[n].get(weight, 1) if n in nbrs else 0))
#        return Degree(dict(d_iter()))

    def selfloops(self):
        return (n for n, nbrs in self._adj.items() if n in nbrs)
