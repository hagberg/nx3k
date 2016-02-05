from collections import Mapping, KeysView, ItemsView, MutableSet

# Notes to help me remember what the ABC classes provide:
# classname | abstract methods -> concrete methods
# which means:
# classname | required methods -> provided methods


# Mapping |getitem, iter, len -> contains, get, keys/values/items, eq, ne
# KeysView | -> init(_mapping), len, iter(keys), contains(keys), _from_iterable 
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class ABCSetMap(Mapping, KeysView):
    def __getitem__(self, key):
        return self._mapping[key]
    def __iter__(self):
        return iter(self._mapping)


# ItemsView | -> init(_mapping), len, iter(items), contains(items), _from_iterable 
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class DataView(ItemsView):
    def __init__(self, nbrs, weight):
        self._mapping = nbrs
        self.weight = weight
    def __getitem__(self, key):
        if key in self._mapping:
            return self._wrap_value(key)
        raise KeyError(key)
    def __iter__(self):
        # For Nodes, key is a node. For Edges, key is a 2-tuple
        for key in self._mapping:
            yield key, self._wrap_value(key)
    def _wrap_value(self, key):
        return self._mapping[key].get(self.weight, None)


# ABCSetMap |-> init(_mapping), getitem, iter, len, contains, get, keys/values/items
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor
class Nodes(ABCSetMap, MutableSet):
    def __init__(self, graph):
        self._graph = graph
        self._mapping = graph._nodes
    def data(self, weight):
        return DataView(self._mapping, weight)
    def selfloops(self):
        return (n for n, nbrs in self._succ.items() if n in nbrs)
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
        nodes = self._mapping
        if n not in nodes:
            self._graph._succ[n] = {} # FIXME factory
            self._graph._pred[n] = {} # FIXME factory
            nodes[n] = attr_dict
            return True # new node
        # update attr even if node already exists
        nodes[n].update(attr_dict)
        return False # not new node
    def discard(self, n):
        try:
            del self._mapping[n]
        except KeyError: # return False if node not present
            return False
        succ = self._graph._succ
        pred = self._graph._pred
        for u in succ[n]:
            del pred[u][n] # remove all edges n-u in digraph
        for u in pred[n]:
            del succ[u][n] # remove all edges n-u in digraph
        del succ[n]          # remove node from succ
        del pred[n]          # remove node from pred
        return True
    def update(self, nodes, **attr):
        for n in nodes:
            try:
                nn, ndict = n
                newdict = attr.copy()
                newdict.update(ndict)
                self.add(nn, **newdict)
            except TypeError:
                self.add(n, attr_dict=None, **attr)
    def clear(self):
        self._graph.e.clear()
        self._mapping.clear()

# Edges
# =====

# ABCSetMap |-> init(_mapping), getitem, iter, len, contains, get, keys/values/items
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor
class Edges(ABCSetMap, MutableSet):
    def __init__(self, graph):
        self._graph = graph
        self._mapping = graph._succ
    def __getitem__(self, ekeys):
        try:
            u,v = ekeys
        except TypeError:
            raise NetworkXError('bad edge key: use edge key = (u,v)')
        try:
            return self._mapping[u][v]
        except KeyError:
            if self._graph._directed:
                raise
            return self._graph._pred[u][v]
    def __iter__(self):
        nodes_nbrs = self._mapping.items()
        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                yield (n, nbr)
    def __len__(self):
        """size of graph"""
        return sum(len(nbrs) for n, nbrs in self._mapping.items())
    def data(self, weight):
        return DataView(self, weight)
    def selfloops(self):
        return ((n, n) for n, nbrs in self._succ.items() if n in nbrs)

    # Mutating Methods
    def _add_edge(self, u, v, attr_dict):
        if not isinstance(attr_dict, Mapping):  # Mapping includes dict
            raise NetworkXError( "The attr_dict argument must be a Mapping.")
        succ = self._mapping
        pred = self._graph._pred
        nodes = self._graph._nodes
        # add nodes
        u_new = u not in succ
        v_new = v not in succ
        if u_new:
            succ[u] = {} # fixme factory
            pred[u] = {} # fixme factory
            nodes[u] = {}
        if v_new:
            succ[v] = {} # fixme factory
            pred[v] = {} # fixme factory
            nodes[v] = {}
        # find the edge
        if not (u_new or v_new):
            if v in succ[u]:
                datadict = succ[u][v]
                datadict.update(attr_dict)
                return False # not new edge
            # if not directed check other direction
            if (not self._graph._directed) and v in pred[u]:
                datadict = pred[u][v]
                datadict.update(attr_dict)
                return False # not new edge
            # else new edge-- drop out of if
        # add new edge
        datadict = attr_dict
        succ[u][v] = datadict
        pred[v][u] = datadict
        return True # new edge

    def add(self, u, v, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        return self._add_edge(u, v, attr_dict)

    def update(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
                dd = dd.copy()
            elif ne == 2:
                u, v = e
                try:
                    {v} # is v hashable, i.e. a datadict?
                except TypeError:
                    dd = v.copy()
                    u,v = u
                else:
                    dd = {}  # doesnt need edge_attr_dict_factory
            else:
                msg = "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,)
                raise NetworkXError(msg)
            dd.update(attr_dict)
            self._add_edge(u, v, dd)

    def discard(self, ekeys):
        try:
            u,v = ekeys
        except TypeError:
            raise NetworkXError('bad edge key: use edge key = (u,v)')
        try:
            del self._graph._succ[u][v]
            del self._graph._pred[v][u]
            return True
        except KeyError:
            return False

    def clear(self):
        succ = self._graph._succ
        pred = self._graph._pred
        for n in self._mapping:
            succ[n].clear()
            pred[n].clear()

# Adjacency
# =========

# ItemsView | -> init(_mapping), len, iter, contains, _from_iterable
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class ABCAtlas(ItemsView):
    """An Atlas is a read-only collection of maps (dict-of-dicts)"""
    def __init__(self, mapping):
        self._mapping = mapping
        self._cache = {}
    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        if key in self._mapping:
            self._cache[key] = wv = self._wrap_value(key)
            return wv
        raise KeyError(key)
    def _wrap_value(self, key):
        return ABCSetMap(self._mapping[key])

class Adjacency(ABCAtlas):
    def list(self, nodelist=None):
        pass # fixme add list
    def matrix(self, nodelist=None, dtype=None, order=None,
                    multigraph_weight=sum, weight='weight', nonedge=0.0):
        pass # fixme add matrix

# Mapping |getitem, iter, len -> contains, get, keys/values/items, eq, ne
class UnionNbrs(Mapping):
    def __init__(self, snbrs, pnbrs, node):
        # keys in both resolve to _mapping but count twice in len
        self._mapping = snbrs
        self._pnbrs = pnbrs
        assert set(snbrs.keys()) & set(pnbrs.keys()) < {node}
    def __getitem__(self, key):
        if key in self._mapping:
            return self._mapping[key]
        return self._pnbrs[key]
    def __iter__(self):
        for n in set(self._mapping) | set(self._pnbrs):
            yield n
    def __len__(self):
        # Note: self-loops make this violate the invariant
        #        len(list(iter(self))) == len(self)
        return len(self._mapping) + len(self._pnbrs)

# ABCSetMap |-> init(_mapping), getitem, iter, len, contains, get, keys/values/items
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class AtlasUnion(ABCSetMap):
    def __init__(self, snbrs, pnbrs):
        assert snbrs.keys() == pnbrs.keys()
        self._mapping = snbrs
        self._pnbrs = pnbrs
    def __getitem__(self, key):
        if key in self._mapping:
            return UnionNbrs(self._mapping[key], self._pnbrs[key], key)



# Graph
# =====

class Graph(ABCSetMap):
    def __init__(self, data=None, **attr):
        self._nodes = nd = {}  # fixme factory
        self._mapping = nd
        self._succ = succ = {}  # fixme factory
        self._pred = pred = {}  # fixme factory
        self._directed = attr.pop("directed", False)
        self.data = {}
        # Interface
        self.n = Nodes(self)
        self.e = Edges(self)
        self.a = Adjacency(AtlasUnion(self._succ, self._pred))
        if self._directed:
            self.su = Adjacency(self._succ)
            self.pr = Adjacency(self._pred)
        else:
            self.su = self.a
            self.pr = self.a
    
    def s(self, nbunch):
        return Subgraph(self, nbunch)
    def clear(self):
        self.n.clear()
        self.e.clear()
        self.data.clear()
    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        return self.__class__(self)
    @property
    def directed(self):
        return self._directed

    def size(self):
        # TODO: weighted
        s = sum(len(nbrs) for n, nbrs in self._succ.items())


# Subgraph
# ========

class SubDict(Mapping):
    def __init__(self, subkey, mapping):
        self._mapping = mapping
        self._subkey = set(subkey) & set(mapping)
    def __getitem__(self, key):
        if key in self._subkey:
            return self._mapping[key]
    def __iter__(self):
        return iter(self._subkey)
    def __len__(self):
        return len(self._subkey)
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self, list(self))

class SubDictOfDict(SubDict):
    def __getitem__(self, key):
        if key in self._subkey:
            return SubDict(self._subkey, self._mapping[key])

class Subgraph(Graph):
    def __init__(self, graph, subnodes):
        self._subnodes = nodes = set(subnodes) & set(graph)
        self._mapping = self._nodes = SubDict(nodes, graph._nodes)
        self._succ = SubDictOfDict(nodes, graph._succ)
        self._pred = SubDictOfDict(nodes, graph._pred)
        self._directed = graph._directed
        self.data = graph.data
        # Interface
        self.n = Nodes(self)
        self.e = Edges(self)
        self.a = Adjacency(AtlasUnion(self._succ, self._pred))
        if self._directed:
            self.su = Adjacency(self._succ)
            self.pr = Adjacency(self._pred)
        else:
            self.su = self.a
            self.pr = self.a


# Degree
# ======

def in_degree(G, weight=None):
    if weight is None:
        return DegreeView(G.pr)
    return WeightedDegreeView(G.pr, weight)

def out_degree(G, weight=None):
    if weight is None:
        return DegreeView(G.su)
    return WeightedDegreeView(G.su, weight)

def degree(G, weight=None):
    if weight is None:
        return DegreeView(G.a)
    return WeightedDegreeView(G.a, weight)

class DegreeView(ItemsView):
    def __init__(self, mapping):
        self._mapping = mapping
    def __getitem__(self, key):
        return len(self._mapping[key])
    def __iter__(self):
        for key, nbrs in self._mapping:
            yield key, len(nbrs)
    def data(self, weight):
        return WeightedDegreeView(self, weight)

class WeightedDegreeView(DataView):
    def _wrap_value(self, key):
        nbrs = self._mapping[key]
        return sum((nbrs[nbr].get(self.weight, 1) for nbr in nbrs))


# Some Testing
# ============

if __name__ == "__main__":
    G = Graph()
    G.n.add(3)
    G.n.update((4, (5,{"color": "red"})))
    G.e.add(2,1)
    G.e.update([(4,6), (7,4,{"weight":2})])
    print("Nodes:", list(G.n))
    print("Nodes with data:", list(G.n.items()))
    print("Nodes with weight:", list(G.n.data("color")))
    print("Edges:", list(G.e))
    print("Edges with data:", list(G.e.data("wt")))
    print("Degree", list(degree(G)))
    print("Neighbors of 2:", list(G.a[2]))
    print("Neighbors of 3:", list(G.a[3]))
    print("Neighbors of 1:", list(G.a[1]))
    print("Neighbors of 4:", list(G.a[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("Directed Graph")
    DG = Graph(directed=True)
    DG.n.add(3)
    G.n.update((4, (5,{"color": "red"})))
    G.e.add(2,1)
    G.e.update([(4,6), (7,4,{"weight":2})])
    print("Nodes:", list(G.n))
    print("Nodes with data:", list(G.n.items()))
    print("Nodes with weight:", list(G.n.data("color")))
    print("Edges:", list(G.e))
    print("Degree", list(degree(G)))
    print("InDegree", list(in_degree(G)))
    print("OutDegree", list(out_degree(G)))
    print("Neighbors of 2:", list(G.a[2]))
    print("Neighbors of 3:", list(G.a[3]))
    print("Neighbors of 1:", list(G.a[1]))
    print("Neighbors of 4:", list(G.a[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("Predecessors of 2:", list(G.pr[2]))
    print("Predecessors of 3:", list(G.pr[3]))
    print("Predecessors of 1:", list(G.pr[1]))
    print("Neighbors of 4:", list(G.a[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("Succcessors of 2:", list(G.pr[2]))
    print("Succcessors of 3:", list(G.su[3]))
    print("Succcessors of 1:", list(G.su[1]))
    print("Neighbors of 4:", list(G.a[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("END OF INITIAL TESTS")

if __name__ == '__main__':
    graph = Graph()
    graph.e.add(1,2,foo='f',bar='b' )
    graph.e.add(2,3,foo='f',bar='b' )
    graph.e.add(3,4,foo='f',bar='b' )
    graph.e.add(4,5)
    print(graph.n)
    print(graph.n.keys())
    print(graph.n.values())
    print(graph.n.items())
    print(graph.n.data("color"))
    print(len(graph.n))
    print(1 in graph.n)
    graph2 = Graph()
    graph2.e.add(0,1)
    graph2.e.add(1,2,foo='f',bar='b' )
    graph2.e.add(2,3)
    graph2.e.add(3,4)
    print(graph.n & graph2.n)

    print(graph.e)
    print(len(graph.e))
    print(graph.e.keys())
    print(graph.e.values())
    print(graph.e.items())
    print(graph.e.data("weight"))
    print([(e,d.get('foo','default')) for (e,d) in graph.e.items()])
    print(dict(graph.e.items()))
    print((2,3) in graph.e)
    print((2,3) in graph.e.keys())
#    print(graph.e & graph2.e)
    print(graph.e[(1,2)])

    print("-- subgraph --")

    graph.n[1]['a']='b'
    s = graph.s([1,2])
    print(s)
    print(s.n)
    print(s.n.items())
    print(s.e)
    print(s.e.keys())
    print(s.e.values())
    print(s.e.items())
    print(s.e.data("weight"))
    print(s.a)

    print(graph.s([1,2]).e.items())
    print([(e,d.get('foo','default')) for (e,d) in graph.s([1,2]).e.items()])
