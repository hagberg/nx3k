# Notes to help remember what the ABC classes provide:
# classname | abstract methods -> concrete methods
# which means:
# classname | required methods -> provided methods

from abc import ABCMeta, abstractmethod
from copy import deepcopy

from collections import Mapping, MappingView, KeysView, ItemsView, MutableSet

# Mapping | getitem, iter, len -> contains, get, keys/values/items, eq, ne
# MappingView | init(_mapping), len, repr
# KeysView | -> init(_mapping), len, iter(keys), contains(keys), _from_iterable
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
# ItemsView | -> init(_mapping), len, iter(items), contains(items), _from_iterable
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor


# KeysView | -> init(_mapping), len, iter(keys), contains(keys), _from_iterable
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class ABCSetMap(KeysView):
    """Provides a read-only "set" object with data associated to elements.
    
    The set and data are based on the initially provided mapping.
    The keys of the mapping form the set, the values provide the data.
    All nonmutable set operations (eq/ne/le/lt/gt/ge/and/or/sub/xor)
    are provided with regular sets returned.

    In addition to set methods, S[key] provides the data for key.
    Finally, you can create a DataView to iterate over wrapped items
    or get wrapped values for given key.

    Parameters
    ==========
    mapping : dict-like
        The keys of this dict are the elements of the set. Values associated
        to those keys provide data associated to the elements of the set.

    Abstract Methods
    ================
    __getitem__ : `S[key]` -> data associated to the set element: `key`

    data : `S.data(wrapper)` -> a DataView on wrapped values of `mapping`

    See Also
    ========
    ABCDataView
    """
    # ABCSetMap |getitem, data -> init(_mapping), iter, len, contains
    #     eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable

    @abstractmethod
    def __getitem__(self, key):
        return self._mapping[key]

    @abstractmethod
    def data(self, weight=None):
        if weight is None:
            return self._mapping.items()
        return DataView(self._mapping, weight)


# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor
# ABCSetMap |getitem, data -> init(_mapping), iter, len, contains
#     eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class ABCMutableSetMap(ABCSetMap, MutableSet):
    """Abstract SetMap class that allows mutation via add/update/discard/remove

    In addition to abstract methods `__getitem__` and `data` as for SetMap,
    this class requires methods `add` and `discard`. From those it supplies
    methods `update`, `remove`, `clear`, `pop` and the in-place set operations.
    """
    # ABCMutableSetMAP | add,discard,getitem,data -> init(_mapping), iter,
    #     len, contains, remove, clear, pop, iand/ior/isub/ixor,
    #     eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
    pass


# MappingView | -> init(_mapping), len, repr
class ABCDataView(MappingView):
    """Abstract class providing a read-only wrapped-value view of a mapping.

    Iteration of the DataView yields (key, wrapped-value) pairs.

    Abstract Methods
    ================
    _wrap_value should be a method that takes a key as an argument and
    returns the desired data based on that key and the _mapping data structure.
    If it returns None, that key is not yielded when iterating over the
    DataView.

    Examples
    ========
    Atlas: When _mapping is a collection of maps, `_wrap_value` can pull out
    a specific value from the inner dict. So `DataView(dict_of_dict, weight)`
    could provide as its wrapped values: `dict_of_dict[key][weight]`

    Filtered values: `_wrap_value` could return `None` when keys don't pass a
    filter. So `DataView(mapping, subset)` could provide values only for keys
    in subset.
    """
    # ABCDataView | _wrap_value -> init(_mapping), len, repr, getitem, iter

    @abstractmethod
    def _wrap_value(self, key):
        return self._mapping[key]

    def __getitem__(self, key):
        return self._wrap_value(key)

    def __iter__(self):
        for key in self._mapping:
            wv = self._wrap_value(self._mapping[key])
            if wv is not None:
                yield key,wv


# ABCDataView | _wrap_value -> init(_mapping), len, repr, getitem, iter
class ABCCachedDataView(ABCDataView):
    """This DataView caches the wrapped values so they only need be wrapped once.

    Abstract Methods
    ================
    _wrap_value should be a method that takes a key as an argument and
    returns the desired data based on that key and the _mapping data structure.
    If it returns None, that key is not yielded when iterating over the
    DataView.

    """
    # ABCCachedDataView | _wrap_value -> init(_mapping), len, repr, getitem, iter
    def __init__(self, mapping):
        self._mapping = mapping
        self._cache = {}

    def __contains__(self, key):
        return key in self._mapping

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        if key in self._mapping:
            self._cache[key] = wv = self._wrap_value(key)
            return wv
        msg = "Not Found: {} cache: {} mapping: {}".format(key, self._cache, self._mapping)
        raise KeyError(msg)

    def __iter__(self):
        for key in self._mapping:
            wv = self[key]
            if wv is not None:
                yield key, wv


class ABCGraphData(object):
    # ABCGraphData | add_node, add_edge, remove_node, remove_edge,
    #        nodes_iter, edges_iter, nodes_data, edges_data,
    #        get_node_data, get_edge_data, successors_iter,
    #        predecessors_iter, neighbors_iter, successors_data,
    #        predecessors_data, neighbors_data,
    #        out_degree, in_degree, degree, order
    #        ->   size, clear, clear_edges
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_node(self, _node, _dd):
        pass
    @abstractmethod
    def add_edge(self, ekeys, _dd):
        pass
    @abstractmethod
    def remove_node(self, _node, _dd):
        pass
    @abstractmethod
    def remove_edge(self, ekeys, _dd):
        pass
    @abstractmethod
    def edges_iter(self, weight_func):
        pass
    @abstractmethod
    def nodes_iter(self, weight_func):
        pass
    @abstractmethod
    def edges_data(self, weight_func):
        pass
    @abstractmethod
    def nodes_data(self, weight_func):
        pass
    @abstractmethod
    def get_edge_data(self, ekeys, weight_func):
        pass
    @abstractmethod
    def get_node_data(self, node, weight_func):
        pass
    @abstractmethod
    def successors_iter(self, _node):
        pass
    @abstractmethod
    def predecessors_iter(self, _node):
        pass
    @abstractmethod
    def neighbors_iter(self, _node):
        pass
    @abstractmethod
    def successors_data(self, _node):
        pass
    @abstractmethod
    def predecessors_data(self, _node):
        pass
    @abstractmethod
    def neighbors_data(self, _node):
        pass
    @abstractmethod
    def out_degree(self, _node):
        pass
    @abstractmethod
    def in_degree(self, _node):
        pass
    @abstractmethod
    def degree(self, _node):
        pass
    @abstractmethod
    def order(self):
        pass

    def size(self):
        deg = self.out_degree
        return sum(deg(n) for n in self.nodes_iter())
    def clear():
        for n in list(self.nodes_iter()):
            self.remove_node(n)
    def clear_edges():
        for ekeys in self.edges_iter():
            self.remove_edge(ekeys)



class ABCGraph(object):
    # ABCGraph | data_structure_factory, successors_structure_factory, 
    #       predecessors_structure_factory, adjacency_structure_factory,
    #       subgraph     ->   nodes, edges, data,
    #       successors, predecessors, adjacency, order,
    #       clear, copy, size, directed, multigraph 
    __metaclass__ = ABCMeta

    @abstractmethod
    def data_structure_factory(self, directed, multigraph):
        return ABCGraphData(directed, multigraph)
    @abstractmethod
    def successors_structure_factory(self):
        pass
    @abstractmethod
    def predecessors_structure_factory(self):
        pass
    @abstractmethod
    def adjacency_structure_factory(self):
        pass

    @abstractmethod
    def subgraph(self, nbunch):
        return ABCSubGraph(self, nbunch)

    def __init__(self, input_graph=None, **kwds):
        self._directed = d = kwds.get("directed", False)
        self._multigraph = m = kwds.get("multigraph", False)
        if input_graph is None:
            nodes,edges = [],[]
        else:
            nodes,egdes = input_graph

        # create graph attributes
        self.data = {}
        if hasattr("data", input_graph):
            self.data.update(input_graph.data)
        self.data.update(kwds)

        # create graph data structure
        self._graph = self.data_structure_factory(d, m)

        # create view objects
        self.edges = Edges(self)
        self.nodes = Nodes(self)
        self.adjacency = Adjacency(self)
        self.successors = Successors(self)
        self.predecessors = Predecessors(self)

        # add input_graph info
        self.nodes.update(nodes)
        self.edges.update(edges)

    def __repr__(self):
        msg = '{0.__class__.__name__}(({1}, {2}), **{3})'
        return msg.format(self, list(self.nodes),
                          list(self.edges), self.data)
    def clear(self):
        self._graph.clear()
        self.data.clear()
    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        return self.__class__(self)
    @property
    def directed(self):
        return self._directed
    @property
    def multigraph(self):
        return self._multigraph
    def size(self, weight=None):
        if weight is None:
            return self._graph.size()
        return sum(wt for ekey,wt in self.edges.data(weight))

class ABCSubGraph(ABCGraph):
    def __init__(self, graph, subnodes):
        self._directed = graph._directed
        self._multigraph = graph._multigraph
        G = graph.data_structure_factory(graph._directed, graph._multigraph)
        self._subnodes = nodes = set(subnodes) & set(graph.nodes)
        G._nodes = SubDict(nodes, graph.nodes)
        G._succ = SubDictOfDict(nodes, graph._graph._succ)
        G._pred = SubDictOfDict(nodes, graph._graph._pred)
        self._graph = G
        self.data = graph.data
        # Interface
        self.nodes = Nodes(self)
        self.edges = Edges(self)
        self.adjacency = Atlas(self.adjacency_structure_factory())
        self.succ = Atlas(self.successors_structure_factory())
        self.pred = Atlas(self.predecessors_structure_factory())


