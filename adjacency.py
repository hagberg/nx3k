from collections import MappingView

class NbrDict(MappingView):
    __slots__ = ["_mapping"]
    # We can return _mapping[n] without wrapper. datadict is read-write
    def __repr__(self):
        return '{0.__class__.__name__}({0._mapping})'.format(self)
    def __iter__(self):
        return iter(self._mapping)
    def __getitem__(self, n):
        return self._mapping[n]
    def __contains__(self, node):
        return node in self._mapping
    def __len__(self):
        return len(self._mapping)

    def keys(self):
        return self._mapping.keys()
    def data(self):
        return self._mapping.values() # Not readonly datadict
    def items(self):
        return self._mapping.items() # Not readonly datadict
    def __eq__(self, other):
        return dict(self.items()) == dict(other.items())
    def __ne__(self, other):
        return not self.__eq__(other)


class Adjacency(NbrDict):
    # __slots__= ["_mapping","_cache"]
    def __init__(self, mapping):
        self._mapping = mapping
        self._cache = {}
    def __iter__(self):
        for n in self._mapping:
            if n in self._cache:
                yield (n, self._cache[n])
            else:
                # NbrDicts are read-only so use wrapper for mapping[n]
                self._cache[n] = nbrdict = NbrDict(self._mapping[n])
                yield n,nbrdict
    def __getitem__(self, n):
        if n in self._cache:
            return self._cache[n]
        if n in self._mapping:
            # NbrDicts are read-only so use wrapper for mapping[n]
            self._cache[n] = nbrdict = NbrDict(self._mapping[n])
            return nbrdict
        raise KeyError
    def data(self):
        # In Python3 we can remove the "set" 
        for n in set(self._mapping.keys()) - set(self._cache.keys()):
            # NbrDicts are read-only so use wrapper for mapping[n]
            self.cache[n] = NbrDict(self.mapping[n])
        return self._cache.values()
    def items(self):
        for n in set(self._mapping.keys()) - set(self._cache.keys()):
            self.cache[n] = NbrDict(self.mapping[n])
        return self._cache.items() # Not readonly datadict

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
