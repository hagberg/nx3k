from collections import Mapping, KeysView, ItemsView, MutableSet
from networkx import NetworkXError
import convert
from copy import deepcopy

# Notes to help me remember what the ABC classes provide:
# classname | abstract methods -> concrete methods
# which means:
# classname | required methods -> provided methods


# Mapping |getitem, iter, len -> contains, get, keys/values/items, eq, ne
# KeysView | -> init(_mapping), len, iter(keys), contains(keys), _from_iterable 
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class ABCSetMap(KeysView, Mapping):
    def __getitem__(self, key):
        return self._mapping[key]
    def __iter__(self):
        return iter(self._mapping)
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True


# ItemsView | -> init(_mapping), len, iter(items), contains(items), _from_iterable 
#  +Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
class DataView(ItemsView):
    def __init__(self, nbrs, weight):
        self._mapping = nbrs
        self.weight = weight
        if not isinstance(weight, str):
            self._wrap_value = weight
    def __getitem__(self, key):
        return self._wrap_value(self._mapping[key])
    def __iter__(self):
        # For Nodes, key is a node. For Edges, key is a 2-tuple
        for key in self._mapping:
            yield key, self._wrap_value(self._mapping[key])
    def _wrap_value(self, value):
        return value.get(self.weight, None)


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
        return (n for n, nbrs in self._graph._succ.items() if n in nbrs)
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
        self._graph._succ.clear()
        self._graph._pred.clear()
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
        except (ValueError,TypeError):
            raise NetworkXError('bad edge key: %s; use edge key = (u,v)' % (ekeys,))
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
        return ((n, n) for n, nbrs in self._graph._succ.items() if n in nbrs)

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
            elif ne == 2:
                u, v = e
                try:
                    {v} # is v hashable, i.e. a datadict?
                except TypeError:
                    dd = v
                    u,v = u
                else:
                    dd = {}  # doesnt need edge_attr_dict_factory
            else:
                msg = "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,)
                raise NetworkXError(msg)
            datadict = attr_dict.copy()
            datadict.update(dd)
            self._add_edge(u, v, datadict)

    def discard(self, ekeys):
        try:
            u,v = ekeys
        except TypeError:
            raise NetworkXError('bad edge key: %s; use edge key = (u,v)' % (ekeys,))
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

class MultiEdges(Edges):
    def __getitem__(self, ekeys):
        try:
            u,v,k = ekeys
        except (TypeError, ValueError):
            try:
                u,v = ekeys
                k = None
            except (TypeError, ValueError):
                raise NetworkXError('bad edge key: %s' % (ekeys,))
        if k is None:
            try:
                keydict = self._mapping[u][v]
            except KeyError:
                if self._graph._directed:
                    raise
                keydict = self._graph._pred[u][v]
            k = next(iter(keydict))
            return keydict[k]
        try:
            return self._mapping[u][v][k]
        except KeyError:
            if self._graph._directed:
                raise
            return self._graph._pred[u][v][k]
    def __iter__(self):
        for n, nbrs in self._mapping.items():
            for nbr, keydict in nbrs.items():
                for k, ddict in keydict.items():
                    yield (n, nbr, k)
    def __len__(self):
        """size of graph"""
        mi = self._mapping.items()
        return sum(len(kd) for n, nbrs in mi for nbr,kd in nbrs.items())
    def data(self, weight):
        return DataView(self, weight)
    def selfloops(self):
        return ((n, n, k) for n, nbrs in self._graph._succ.items()
                          if n in nbrs
                          for nbr, kd in nbrs.items()
                          for k in kd)
    # Mutating Methods
    def _add_edge(self, u, v, k, attr_dict):
        if not isinstance(attr_dict, Mapping):  # Mapping includes dict
            raise NetworkXError( "The attr_dict argument must be a Mapping.")
        succ = self._mapping
        pred = self._graph._pred
        nodes = self._graph._nodes
        # add nodes
        u_new = u not in succ
        v_new = v not in succ
        if u_new:
            succ[u] = {}  # fixme factory
            pred[u] = {}  # fixme factory
            nodes[u] = {}
        if v_new:
            succ[v] = {}  # fixme factory
            pred[v] = {}  # fixme factory
            nodes[v] = {}
        # find the edge
        if not (u_new or v_new):
            new_succ = new_pred = False
            if v in succ[u]:
                skeydict = succ[u][v]
                if k in skeydict:
                    datadict = skeydict[k]
                    datadict.update(attr_dict)
                    return False  # not new edge
                # add edge to keydict
                if k is None:
                    k = len(skeydict)
                    while k in skeydict:
                        k += 1
                datadict = attr_dict
                skeydict[k] = datadict
                return True  # New edge
            # if not directed check other direction
            if (not self._graph._directed) and v in pred[u]:
                pkeydict = pred[u][v]
                if k in pkeydict:
                    datadict = pkeydict[k]
                    datadict.update(attr_dict)
                    return False  # not new edge
                # add edge to keydict
                if k is None:
                    k = len(pkeydict)
                    while k in pkeydict:
                        k += 1
                datadict = attr_dict
                pkeydict[k] = datadict
                return True  # New edge
            # else new edge-- drop out of if
        # add new edge
        k = 0 if k is None else k
        datadict = attr_dict
        keydict = {k: datadict}  # fixme factory
        succ[u][v] = keydict
        pred[v][u] = keydict
        return True # new edge

    def add(self, u, v, k=None, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        return self._add_edge(u, v, k, attr_dict)

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
            if ne == 4:
                u, v, k, dd = e
            elif ne == 2:
                u, v = e
                try:
                    {v} # is v hashable, i.e. a datadict?
                except TypeError:
                    dd = v
                    if len(u) == 3:
                        u, v, k = u
                    else:
                        u, v = u
                        k = None
                else:
                    k = None
                    dd = {}  # doesnt need edge_attr_dict_factory
            elif ne == 3:
                u, v, k = e
                try:
                    {k} # is k hashable, i.e. a datadict?
                except TypeError:
                    dd = k
                    k = None
                else:
                    dd = {}
            else:
                msg = "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,)
                raise NetworkXError(msg)
            datadict = attr_dict.copy()
            datadict.update(dd)
            self._add_edge(u, v, k, datadict)

    def discard(self, ekeys):
        try:
            u,v,k = ekeys
        except (TypeError, ValueError):
            try:
                u,v = ekeys
            except (TypeError, ValueError):
                raise NetworkXError('bad edge key: %s' % (ekeys,))
            if u in self._graph._succ and v in self._graph._succ[u]:
                keydict = self._graph._succ[u][v]
                keydict.popitem()
                if len(keydict) == 0:
                    del self._graph._succ[u][v]
                    del self._graph._pred[v][u]
                return True
            elif self._graph._directed is False\
                    and v in self._graph._pred\
                    and u in self._graph._pred[v]:
                keydict = self._graph._pred[u][v]
                keydict.popitem()
                if len(keydict) == 0:
                    del self._graph._pred[u][v]
                    del self._graph._succ[v][u]
                return True
            return False  # Didn't remove edge
        try:
            del self._graph._succ[u][v]
            del self._graph._pred[v][u]
            return True
        except KeyError:
            if self._graph._directed is True:
                return False
            try:
                del self._graph._pred[u][v]
                del self._graph._succ[v][u]
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
class ABCAtlas(ABCSetMap):
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

class ABCMultiAtlas(ABCAtlas):
    def _wrap_value(self, key):
        return ABCAtlas(self._mapping[key])

class Adjacency(ABCAtlas):
    def list(self, nodelist=None):
        pass # fixme add list
    def matrix(self, nodelist=None, dtype=None, order=None,
                    multigraph_weight=sum, weight='weight', nonedge=0.0):
        pass # fixme add matrix

class MultiAdjacency(ABCMultiAtlas, Adjacency):
    pass

# Mapping |getitem, iter, len -> contains, get, keys/values/items, eq, ne
class NbrsUnion(Mapping):
    def __init__(self, snbrs, pnbrs, node):
        # keys in both resolve to _mapping but count twice in len
        self._mapping = snbrs
        self._pnbrs = pnbrs
        assert set(snbrs.keys()) & set(pnbrs.keys()) <= {node}
    def __getitem__(self, key):
        if key in self._mapping:
            return self._mapping[key]
        return self._pnbrs[key]
    def __iter__(self):
        for n in self._mapping:
            yield n
        for n in self._pnbrs:
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
            return NbrsUnion(self._mapping[key], self._pnbrs[key], key)
        raise KeyError(key)

# NbrsUnion | -> init(_mapping), getitem, iter, len, contains, get, keys/values/items, eq, ne
class MultiNbrsUnion(NbrsUnion):
    def __getitem__(self, key):
        if key in self._mapping:
            return ABCSetMap(self._mapping[key])
        return ABCSetMap(self._pnbrs[key])

# AtlasUnion |-> init(_mapping), getitem, iter, len, contains, get, keys/values/items
#               eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint, _from_iterable
class MultiAtlasUnion(AtlasUnion):
    def __getitem__(self, key):
        if key in self._mapping:
            return MultiNbrsUnion(self._mapping[key], self._pnbrs[key], key)
        raise KeyError(key)



# Graph
# =====

#class MultiGraph(Graph):
#    AtlasUnion = MultiAtlasUnion
#    Edges = MultiEdges
#    Adjacency = MultiAdjacency
class Graph(ABCSetMap):
    def __init__(self, data=None, **attr):
        self._nodes = nd = {}  # fixme factory
        self._mapping = nd
        self._succ = succ = {}  # fixme factory
        self._pred = pred = {}  # fixme factory
        self._directed = attr.pop("directed", False)
        self._multigraph = attr.pop("multigraph", False)
        if self._multigraph:
            myEdges = MultiEdges
            myAdjacency = MultiAdjacency
            myAtlasUnion = MultiAtlasUnion
        else:
            myEdges = Edges
            myAdjacency = Adjacency
            myAtlasUnion = AtlasUnion
        # Interface
        self.n = Nodes(self)
        self.e = myEdges(self)
        self.a = myAdjacency(myAtlasUnion(self._succ, self._pred))
        if self._directed:
            self.su = myAdjacency(self._succ)
            self.pr = myAdjacency(self._pred)
        else:
            self.su = self.a
            self.pr = self.a
        # graph data attributes
        self.data = attr
        # Handle input
        if data is None:
            return
        if hasattr(data, "_nodes"):
            # new datadicts but with same info (containers in datadicts same)
            self.data.update(data.data)
            for n in data.n:
                self.n.update(data.n.items())
            self.e.update(data.e.items())
        elif len(data) == 2:
            try:
                V,E = data
                self.n.update(V)
                self.e.update(E)
            except:  # something else
                d=self.data.copy()
                convert.to_networkx_graph(data, create_using=self)
                self.data.update(d)
        else:
            msg = ("Graph argument must be a graph "
                   "or (V, E)-tuple of nodes and edges.")
            raise NetworkXError(msg)
    
    def __repr__(self):
        return '{0.__class__.__name__}({1}, {2})'.format(self, list(self.n), list(self.e))

    def s(self, nbunch):
        return Subgraph(self, nbunch)
    def clear(self):
        self.n.clear()
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
            return len(self.e)
        return sum(wt for wt in self.e.data(weight).values())


# Subgraph
# ========

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

class SubDictOfDictOfDict(SubDict):
    def __getitem__(self, key):
        if key in self._subkey:
            return SubDictOfDict(self._subkey, self._mapping[key])
        raise KeyError(key)

class Subgraph(Graph):
    def __init__(self, graph, subnodes):
        self._multigraph = graph._multigraph
        if self._multigraph:
            myEdges = MultiEdges
            myAdjacency = MultiAdjacency
            myAtlasUnion = MultiAtlasUnion
            mySubDictOfDict = SubDictOfDictOfDict
        else:
            myEdges = Edges
            myAdjacency = Adjacency
            myAtlasUnion = AtlasUnion
            mySubDict = SubDict
            mySubDictOfDict = SubDictOfDict
        self._directed = graph._directed
        self._subnodes = nodes = set(subnodes) & set(graph)
        self._mapping = self._nodes = SubDict(nodes, graph._nodes)
        self._succ = mySubDictOfDict(nodes, graph._succ)
        self._pred = mySubDictOfDict(nodes, graph._pred)
        self.data = graph.data
        # Interface
        self.n = Nodes(self)
        self.e = myEdges(self)
        self.a = myAdjacency(myAtlasUnion(self._succ, self._pred))
        if self._directed:
            self.su = myAdjacency(self._succ)
            self.pr = myAdjacency(self._pred)
        else:
            self.su = self.a
            self.pr = self.a


# Degree
# ======

def in_degree(G, weight=None):
    if not G.multigraph:
        return DegreeView(G.pr, weight)
    return MultiDegreeView(G.pr, weight)

def out_degree(G, weight=None):
    if not G.multigraph:
        return DegreeView(G.su, weight)
    return MultiDegreeView(G.su, weight)

def degree(G, weight=None):
    if not G.multigraph:
        return DegreeView(G.a, weight)
    return MultiDegreeView(G.a, weight)

class DegreeView(DataView):
    def __init__(self, mapping, weight):
        self._mapping = mapping
        if weight is None:
            self._wrap_value = len
        elif isinstance(weight, str):
            self._wrap_value = lambda nbrs: \
                    sum((nbrs[nbr].get(weight, 1) for nbr in nbrs))
        else:  # weight is callable
            self._wrap_value = weight
    def __iter__(self):
        for key,nbrs in self._mapping:
            yield key, self._wrap_value(nbrs)

class MultiDegreeView(DataView):
    def __init__(self, mapping, weight):
        self._mapping = mapping
        if weight is None:
            self._wrap_value = lambda nbrs: \
                    sum(len(keydict) for nbr,keydict in nbrs.items())
        elif isinstance(weight, str):
            self._wrap_value = lambda nbrs: \
                    sum(sum(keydict[k].get(weight, 1) for k in keydict)
                        for nbr,keydict in nbrs.items())
        else:  # weight is callable
            self._wrap_value = weight
    def __iter__(self):
        for key,nbrs in self._mapping.items():
            yield key, self._wrap_value(nbrs)
        


# Some Testing
# ============

if __name__ == "__main__":
    G = Graph(multigraph=True)
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
    print(G.a[4])
    print(G.a[4].values())
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("Directed Graph")
    DG = Graph(directed=True, multigraph=True)
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
    print("Neighbors of 4:", list(G.pr[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("Successors of 2:", list(G.su[2]))
    print("Successors of 3:", list(G.su[3]))
    print("Successors of 1:", list(G.su[1]))
    print("Successors of 4:", list(G.su[4]))
    print("Neighbors with data of 4:", list(G.a[4].values()))
    print("END OF INITIAL TESTS")

if __name__ == '__main__':
    graph = Graph(multigraph=True)
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
    graph2 = Graph(multigraph=True)
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
    print("same graph?",list(graph.e),list(graph2.e))
    print("edge-or:",graph.e | graph2.e)
    print("edge-and:",graph.e & graph2.e)
    print("edge-xor:",graph.e ^ graph2.e)
    print(graph.e[(1,2,0)])

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
