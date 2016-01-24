from collections import MappingView
import networkx as nx

class Adjacency(MappingView):
    def __getitem__(self, key):
        return self._mapping[key]
    def __iter__(self):
        for n,nbrs in self._mapping.items():
            yield n,nbrs
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._mapping.items()))

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
