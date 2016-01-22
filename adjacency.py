from collections import MappingView

class Adjacency(MappingView):
    def __getitem__(self, key):
        return self._mapping[key]
    def __iter__(self):
        for n,nbrs in self._mapping.items():
            yield n,nbrs
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self._mapping.items()))
