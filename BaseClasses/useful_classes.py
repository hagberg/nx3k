# Notes to help remember what the ABC classes provide:
# classname | abstract methods -> concrete methods
# which means:
# classname | required methods -> provided methods

from collections import Mapping#, MappingView, KeysView, ItemsView, MutableSet
from abstract_classes import ABCCachedDataView

# Mapping |getitem, iter, len -> contains, get, keys/values/items, eq, ne
class UnionMap(Mapping):
    """A read-only map that is a union of two maps.

    If a key is not in `map1` we look in `map2`.
    Iteration is over both sets of keys (so keys may be repeated).
    Length is computed as the sum of the lengths of two maps.
    """
    def __init__(self, map1, map2):
        # keys in both maps resolve to value in map1 but still count twice in len
        self._mapping = map1
        self._backup = map2
        #assert set(map1.keys()) & set(map2.keys()) <= {node}
    def __getitem__(self, key):
        if key in self._mapping:
            return self._mapping[key]
        return self._backup[key]
    def __iter__(self):
        for n in self._mapping:
            yield n
        for n in self._backup:
            yield n
    def __len__(self):
        return len(self._mapping) + len(self._backup)


# SetMap |-> init(_mapping), getitem, iter, len, contains, get, keys/values/items
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class UnionAtlas(ABCCachedDataView):
    """A read-only collection of maps that combines values.

    The two input maps should have identical keys. The values
    should themselves be maps (like a dict-of-dict structure). 
    A lookup in the UnionAtlas returns a UnionMap of the two
    maps found as values. Since input map order matters for UnionMap,
    order matters for UnionAtlas as well. The value maps in the
    first map come first in the UnionMap.

    This structure allows two dict-of-dicts to appear as one.
    One example use is to provide neighbors from a successors
    dict-of-dict and a predecessors dict-of-dict.
    """
    def __init__(self, snbrs, pnbrs):
        assert snbrs.keys() == pnbrs.keys()
        self._mapping = snbrs
        self._pnbrs = pnbrs
        self._cache = {}
    def _wrap_value(self, key):
        return UnionMap(self._mapping[key], self._pnbrs[key])


class SubDict(Mapping):
    def __init__(self, subkey, mapping):
        self._mapping = mapping
        self._subkey = set(subkey) & set(mapping)
    def __getitem__(self, key):
        if key in self._subkey:
            return self._mapping[key]
        raise KeyError(key)
    def __iter__(self):
        return iter(self._subkey)
    def __len__(self):
        return len(self._subkey)
    def __repr__(self):
        return '{0.__class__.__name__}({1}, {2})'.format(self, list(self._subkey), list(self._mapping))

class SubDictOfDict(SubDict):
    def __getitem__(self, key):
        if key in self._subkey:
            return SubDict(self._subkey, self._mapping[key])
        raise KeyError(key)
