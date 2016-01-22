from collections import MappingView,KeysView,ValuesView,ItemsView
from networkx.exception import NetworkXError

# consider other mutable set methods?
# s.update(t)   s |= t  return set s with elements added from t
# s.intersection_update(t)      s &= t  return set s keeping only elements also found in t
# s.difference_update(t)        s -= t  return set s after removing elements found in t
# s.symmetric_difference_update(t)      s ^= t  return set s with elements from s or t but not both
# s.add(x)              add element x to set s
# s.remove(x)           remove x from set s; raises KeyError if not present
# s.discard(x)          removes x from set s if present
# s.pop()               remove and return an arbitrary element from s; raises KeyError if empty
# s.clear()             remove all elements from set s

class Nodes(object):
    __slots__ = ('_nodes','_adj')
    def __init__(self, nodes, adj):
        self._nodes = nodes
        self._adj = adj
    def __iter__(self):
        for n in self._nodes:
            yield n
    def __getitem__(self, key):
        return self._nodes[key]
    def __contains__(self, key):
        return key in self._nodes
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._nodes.keys()))
    def __len__(self):
        return len(self._nodes)
    def __and__(self, other):
        return set(self._nodes) & set(other)
    def __or__(self, other):
        return set(self._nodes) | set(other)
    def __xor__(self, other):
        return set(self._nodes) ^ set(other)
    def __sub__(self, other):
        return set(self._nodes) - set(other)
    def __isub__(self, nodes):
        return self.difference_update(nodes)
#        if it is self:
#            self.clear()
#        else:
#            for value in it:
#                self.remove(value)
#        return self
    def difference_update(self, nodes):
        for n in nodes:
            try:
                self.remove(n)
            except NetworkXError: # shouldn't silently drop error here
                pass
        return self

    def keys(self):
        return NodeKeys(self._nodes)
    def data(self):
        return NodeData(self._nodes)
    def items(self):
        return NodeItems(self._nodes)
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

    def update(self, nodes, **attr):
        for n in nodes:
            try:
                nn, ndict = n
                newdict = attr.copy()
                newdict.update(ndict)
                self.add(nn, **newdict)
            except TypeError:
                self.add(n, attr_dict=None, **attr)

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


class NodeKeys(KeysView):
    def __repr__(self):
        return '{}'.format(list(self._mapping))

class NodeData(ValuesView):
    def __repr__(self):
        return '{}'.format(list(self._mapping.values()))

class NodeItems(ItemsView):
    def __repr__(self):
        return '{}'.format(list(self._mapping.items()))
