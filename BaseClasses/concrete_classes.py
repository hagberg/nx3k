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

from abstract_classes import ABCSetMap, ABCMutableSetMap, ABCGraph
    # ABCSetMap |getitem, data -> init(_mapping), iter, len, contains
    #     eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
    # ABCMutableSetMAP | add,discard,getitem,data -> init(_mapping), iter,
    #     len, contains, remove, clear, pop, iand/ior/isub/ixor,
    #     eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
    # ABCGraph | data_structure_factory, successors_structure_factory, 
    #       predecessors_structure_factory, adjacency_structure_factory,
    #       subgraph     ->   nodes, edges, data,
    #       successors, predecessors, adjacency, order,
    #       clear, copy, size, directed, multigraph 
from abstract_classes import ABCDataView, ABCCachedDataView
    # ABCDataView | _wrap_value -> init(_mapping), len, repr, getitem, iter
    # ABCCachedDataView | _wrap_value -> init(_mapping), len, repr, getitem, iter
from useful_classes import UnionMap, UnionAtlas

class SetMap(ABCSetMap):
    """A read-only set of keys with associated datadicts for each key.

    Parameters
    ==========
    mapping : dict-of-datadicts
        a map with keys acting as elements of a set and values 
        that hold data associated with that element. Typically
        the value is a datadict with (attribute, value) entries.
        But it could be an object that returns a single numeric
        value from a vector indexed by the key. For Networkx,
        this class is used to serve data attributes for nodes
        (keyed by node to data) and also edges (keyed by edge
        tuples to data).

    See Also
    ========
    DataView

    """
    def __getitem__(self, key):
        return self._mapping[key]
    def data(self, weight=None):
        if weight is None:
            return self._mapping.items()
        return DataView(self._mapping, weight)

class Atlas(ABCCachedDataView):
    """A Read-only View of a collection of maps. 

    One can think of this class as a dict of `SetMap`s.
    Keys indicate which map to look at. Values are read-only
    SetMap wrappers of that map. The wrapped inner maps are
    cached for future recall.

    This class is used to provide Adjacency structures for
    fast traversal of the network. Successors and Predecessors
    also use this class.
    """
    def _wrap_value(self, key):
        return SetMap(self._mapping[key])


# ItemsView | -> init(_mapping), len, iter(items), contains(items), _from_iterable
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class DataView(ABCDataView):
    """Provides a read-only wrapped view of an Atlas (map-of-maps).

    Parameters
    ==========
    mapping : map
        The keys of mapping indicate which inner map to look up.
        The values hold the inner map.

    weight : string or method
        If a string, then treat the values (the inner mappings) as
        datadicts. The string is looked up in the datadict and value returned.
        If a method, it should take `self` and `key` as inputs and return
        a wrapped value representing the data requested for that key.

    Examples
    ========
    >>> atlas = {1: {"color": "b", "size": 3}, 2: {"color": "r", "size": 4}}
    >>> color = DataView(atlas, "color")
    >>> color[1]
    "b"
    >>> list(color)
    [(1, "b"), (2, "r")]

    """
    def __init__(self, mapping, weight):
        self._mapping = mapping
        if callable(weight):
            self._wrapper = weight
        else:
            self._wrapper = lambda dd: dd.get(weight, None)
    def _wrap_value(self, dd):
        return self._wrapper(dd)


# ABCMutableSetMap | getitem, data, add, discard -> init(_mapping), iter, len, contains
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class Nodes(ABCMutableSetMap):
    def __init__(self, graph):
        self._graph = graph._graph
        self._mapping = graph._graph._nodes
    
    def __getitem__(self, node):
        return self._mapping[node]

    def data(self, weight=None):
        if weight is None:
            return self._mapping.items()
        return DataView(self._mapping, weight)
    
    # Mutating Methods
    def add(self, n, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                msg = "The attr_dict argument must be a dictionary."
                raise NetworkXError(msg)
        self._graph.add_node(n, attr_dict)

    def discard(self, n):
        try:
            self._graph.discard_node(n)
        except KeyError:
            return

    def update(self, nodes, **attr):
        for n in nodes:
            try:
                nn, ndict = n
                newdict = attr.copy()
                newdict.update(ndict)
                self._graph.add_node(nn, newdict)
            except TypeError:
                self._graph.add_node(n, attr)
    
    def clear(self):
        self._graph.clear_nodes()

# Edges
# =====

# MutableSetMap | getitem, data, add, discard -> init(_mapping), iter, len, contains
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class Edges(ABCMutableSetMap):
    def __init__(self, graph):
        self._graph = graph._graph
        self._mapping = graph._graph._succ

    def __getitem__(self, ekeys):
        try:
            u,v = ekeys
        except (ValueError, TypeError):
            raise NetworkXError('bad edge key: {} use edge key = (u,v)'.format(ekeys))
        return self._graph.get_edge_data((u,v),lambda x:x)
    def __contains__(self, ekeys):
        try:
            self[ekeys]
        except:
            return False
        return True
    def __iter__(self):
        return self._graph.edges_iter()
    def __len__(self):
        return self._graph.size()
    def data(self, weight=None):
        if weight is None:
            return ItemsView(self)
        return DataView(self, weight)

    def selfloops(self):
        return ((n, n) for n,nbrs in self._graph.successors_iter()
                if n in nbrs)

    # Mutating Methods
    def add(self, u, v, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise TypeError(
                    "The attr_dict argument must be a dictionary.")
        return self._graph.add_edge((u, v), attr_dict)

    def update(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise TypeError(
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            u,v = e
            try:
                {v}
            except (TypeError, ValueError):
                dd = v
                if len(u) == 3:
                    u,v,k = u
                else:
                    u,v = u
            else:
                dd = {}
            datadict = attr_dict.copy()
            datadict.update(dd)
            self._graph.add_edge((u, v), datadict)

    def discard(self, ekeys):
        try:
            self._graph.remove_edge(ekeys)
        except KeyError:
            pass

    def clear(self):
        self._graph.clear_edges()

# Adjacency
# =========
#
#class Adjacency(Atlas):
#    def list(self, nodelist=None):
#        pass # fixme add list
#    def matrix(self, nodelist=None, dtype=None, order=None,
#                    multigraph_weight=sum, weight='weight', nonedge=0.0):
#        pass # fixme add matrix
#

from backend_dod import DodGraphData

# Graph
# =====

class Graph(ABCGraph):

    def data_structure_factory(self, directed, multigraph):
        return DodGraphData(directed, multigraph)
    def successors_structure_factory(self):
        return {}
    def predecessors_structure_factory(self):
        return {}
    def adjacency_structure_factory(self):
        return {}

    def subgraph(self, nbunch):
        return SubGraph(self, nbunch)

    def __init__(self, input_sets=None, **attr):
        self._directed = attr.pop("directed", False)
        self._multigraph = attr.pop("multigraph", False)
        self._graph = self.data_structure_factory(self._directed,
                self._multigraph)
        #self._nodes = nd = {}  # fixme factory
        #self._mapping = nd
        #self._succ = succ = {}  # fixme factory
        #self._pred = pred = {}  # fixme factory
        # Interface
        self.nodes = Nodes(self)
        self.edges = Edges(self)
        self.adjacency = Atlas(UnionAtlas(self._graph._succ, self._graph._pred))
        if self._directed:
            self.succ = Atlas(self._graph._succ)
            self.pred = Atlas(self._graph._pred)
        else:
            self.succ = self.adjacency
            self.pred = self.adjacency
        # graph data attributes
        self.data = attr
        # Handle input
        if input_sets is not None:
            (nodes, edges) = input_sets
            self.nodes.update(nodes)
            self.edges.update(edges)
            if hasattr("data", input_sets):
                self.data.update(input_sets.data)
    def __iter__(self):
        yield self.nodes
        yield self.edges
    def __repr__(self):
        return '{0.__class__.__name__}({1}, {2})'.format(self, list(self.nodes), list(self.edges))

    def clear(self):
        self.nodes.clear()
        self.data.clear()
    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        return self.__class__(self)
    @property
    def directed(self):
        return self._directed

from useful_classes import SubDict, SubDictOfDict

class SubGraph(Graph):
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

    
