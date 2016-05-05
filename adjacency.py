from collections import Mapping, KeysView, ValuesView, ItemsView, Set

# no ABC has repr so we should provide it
# Mapping -> getitem, len, iter
# MutableMapping -> setitem, delitem, getitem, len, iter
#
# MappingView takes a dict as input, stores it as self._mapping
#     and creats a read-only interface.
# KeyView and friends add Set operations acting on the output of iter
#     to make that work they redefine @classmethod _from_iterable(self, it)
#     as  return set(it)    so the result of the set operations is a set
class SuccDict(Mapping, Set):
    __slots__ = ["_nbrs"]
    @classmethod
    def _from_iterable(self, it):
        return set(it)   # result of set operations is a builtin set
    def __init__(self, nbrs):
        self._nbrs = nbrs
    def __getitem__(self, node):
        return self._nbrs[node]
    def __iter__(self):
        return iter(self._nbrs)
    def __len__(self):
        return len(self._nbrs)
    def __repr__(self):
        return '{0.__class__.__name__}({list(0)})'.format(self)
# no more methods needed, but these seem reasonable
    def __contains__(self, node):
        return node in self._nbrs
# All rest supplied by Mapping Superclass
#    def keys(self):
#        return KeysView(self)
#    def values(self):
#        return ValuesView(self)
#    def data(self):
#        return ValuesView(self)
#    def items(self):
#        return ItemsView(self)
#    def __eq__(self, other):
#        return dict(self.items()) == dict(other.items())
#    def __ne__(self, other):
#        return not self.__eq__(other)
#    def get(self, key, default=None):
#        try:
#            return self[key]
#        except KeyError:
#            return default

class PredDict(SuccDict):
    """Same as SuccDict, just call with self._pred instead of self._succ"""
    pass

class NbrDict(SuccDict):
    __slots__= ["_snbrs","_pnbrs"]
    def __init__(self, snbrs, pnbrs):
        self._snbrs = snbrs
        self._pnbrs = pnbrs
    def __getitem__(self, nbr):
        try:
            return self._snbrs[nbr]
        except KeyError:
            return self._pnbrs[nbr]
    def __iter__(self):
        nbrs_bag = (self._snbrs, self._pnbrs)
        return (n for nbrs in nbrs_bag for n in nbrs)
    def __len__(self):
        return len(self._snbrs) + len(self._pnbrs)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
# no more methods needed, but these seem reasonable
    def __contains__(self, nbr):
        return (nbr in self._snbrs) or (nbr in self._pnbrs)


class Adjacency(Mapping):
    # __slots__= ["_succ", "_pred", "_cache", "_directed"]
    def __init__(self, succ, pred):
        self._succ = succ
        self._pred = pred
        self._cache = {} # dict of node -> NbrDict
    def _nbr_object(self, n):
        return NbrDict(self._succ[n], self._pred[n])
    def __getitem__(self, n):
        if n in self._cache:
            return self._cache[n]
        if n in self._succ:
            self._cache[n] = nbrdict = self._nbr_object(n)
            return nbrdict
        raise KeyError
    def __iter__(self):
        cache = self._cache
        for n in self._succ:
            if n in cache:
                yield n,cache[n]
            else:
                cache[n] = nbrdict = self._nbr_object(n)
                yield n,nbrdict
    # user should never need __len__, but Mapping methods do
    def __len__(self):
        return len(self._succ)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
# This really isn't data, its a dict of neighbors
#    def data(self):
#        for n in set(self._succ) - set(self._cache):
#            self._cache[n] = self._nbr_object(n)
#        return self._cache.values()
    def items(self):
        for n in set(self._succ) - set(self._cache):
            self._cache[n] = self._nbr_object(n)
        return self._cache.items()

    def list(self, nodelist=None):
        if nodelist is None:
            nodelist = list(n for n,nbrs in self)
        nodeset = set(nodelist)
        if len(nodelist) != len(nodeset):
            msg = "Ambiguous ordering: `nodelist` contained duplicates."
            raise nx.NetworkXError(msg)
        nlen = len(nodelist)
        index = dict(zip(nodelist,range(nlen)))
        l = []
        for n in nodelist:
              l.append([index[nbr] for nbr in self[n]])
        return l

    def matrix(self, nodelist=None, dtype=None, order=None,
                    multigraph_weight=sum, weight='weight', nonedge=0.0):
        import numpy as np
        if nodelist is None:
            nodelist = list(n for n,nbrs in self)
        nodeset = set(nodelist)
        if len(nodelist) != len(nodeset):
            msg = "Ambiguous ordering: `nodelist` contained duplicates."
            raise nx.NetworkXError(msg)
        nlen=len(nodelist)
        index=dict(zip(nodelist,range(nlen)))
        M = np.zeros((nlen,nlen), dtype=dtype, order=order) + np.nan
        for u,nbrdict in self:
            for v,d in nbrdict.items():
                try:
                    M[index[u],index[v]] = d.get(weight,1)
                except KeyError:
                    # This occurs when there are fewer desired nodes than
                    # there are nodes in the graph: len(nodelist) < len(G)
                    pass

        M[np.isnan(M)] = nonedge
        M = np.asmatrix(M)
        return M

class Successors(Adjacency):
    # __slots__= ["_succ", "_pred", "_cache", "_directed"]
    def __init__(self, succ):
        self._succ = succ
        self._cache = {}
    def _nbr_object(self, n):
        return SuccDict(self._succ[n])
class Predecessors(Successors):
    """Same as Successors, but you pass it self._pred"""
    pass
