from collections import MutableMapping, Mapping, MutableSet, Set, KeysView, ItemsView
#from networkx import NetworkXError
NetworkXError = Exception
from ABCgraph import Adjacency, AtlasUnion

class Edge(object):
    def __init__(self, node0, node1, **kwds):
        self.data = kwds
        self.node0 = node0
        self.node1 = node1
    def __getitem__(self, n):
        if n == 0:
            return self.node0
        if n == 1:
            return self.node1
        raise KeyError(n)
    def __iter__(self):
        yield self.node0
        yield self.node1
    def __len__(self):
        return 2
    def __eq__(self, other):
        return set(other) == set(self)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return "{0.__class__.__name__}({0.node0}, {0.node1})".format(self)
    def __hash__(self):
        return hash(frozenset((self.node0,self.node1)))

def asEdge(obj, **kwds):
    if isinstance(obj, Edge):
        obj.data.update(kwds)
        return obj
    try:
        u,v = obj
    except (TypeError, ValueError):
        raise NetworkXError("Edge object must be length 2: {}".format(obj))
    return Edge(u, v, **kwds)

class DiEdge(Edge):
    def __eq__(self, other):
        return tuple(self) == tuple(other)
    def __hash__(self):
        return hash((self.node0, self.node1))

def asDiEdge(obj, **kwds):
    if isinstance(obj, DiEdge):
        obj.data.update(kwds)
        return obj
    try:
        u,v = obj
    except (TypeError, ValueError):
        raise NetworkXError("DiEdge object must be length 2: {}".format(obj))
    return DiEdge(u, v, **kwds)

class MultiEdge(Edge):
    def __init__(self, node0, node1, edgekey, **kwds):
        super(MultiEdge, self).__init__(node0, node1, **kwds)
        self.edgekey = edgekey
    def __getitem__(self, n):
        if n == 0:
            return self.node0
        if n == 1:
            return self.node1
        if n in ("edgekey", "key", "k", 2):
            return self.edgekey
        return self.__dict__(n)
    def __iter__(self):
        yield self.node0
        yield self.node1
        yield self.edgekey
    def __len__(self):
        return 3
    def __eq__(self, other):
        return (set(other[:2]) == set(self[:2])) and (self[2] == other[2])
    def __repr__(self):
        return "{0.__class__.__name__}({{0.node0}, {0.node1}}, {0.edgekey})".format(self)
    def __hash__(self):
        return hash((frozenset((self.node0,self.node1)),self.edgekey))
    # Mutation Methods

def asMultiEdge(obj, **kwds):
    if isinstance(obj, MultiEdge):
        obj.data.update(kwds)
        return obj
    try:
        u,v,k = obj
    except (TypeError, ValueError):
        raise NetworkXError("MultiEdge object must be length 3: {}".format(obj))
    return MultiEdge(u, v, k, **kwds)


class MultiDiEdge(MultiEdge):
    def __eq__(self, other):
        return (tuple(other[:2]) == tuple(self[:2])) and (self[2] == other[2])
    def __repr__(self):
        return "{0.__class__.__name__}(({0.node0}, {0.node1}), {0.edgekey})".format(self)
    def __hash__(self):
        return hash(((self.node0, self.node1), self.edgekey))

def asMultiDiEdge(obj, **kwds):
    if isinstance(obj, MultiDiEdge):
        obj.data.update(kwds)
        return obj
    try:
        u,v,k = obj
    except (TypeError, ValueError):
        raise NetworkXError("MultiDiEdge object must be length 3: {}".format(obj))
    return MultiDiEdge(u, v, k, **kwds)


class Node(object):
    def __init__(self, obj, **kwds):
        self.data = kwds
        self.node0 = obj
    def __getitem__(self, key):
        if key == 0:
            return self.node0
        raise KeyError(key)
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.node0 == other.node0
        return self.node0 == other
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return "Node({})".format(self.node0)
    def __hash__(self):
        return hash(self.node0)

def asNode(obj, **kwds):
    if isinstance(obj, Node):
        obj.data.update(kwds)
        return obj
    return Node(obj, **kwds)

# Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor
class Nodes(MutableSet):
    @classmethod
    def _from_iterable(self, it):
        return set(it)
    def __init__(self, graph, nodes):
        self._graph = graph
        self._nodeset = set(asNode(n) for n in nodes)
        self._nodedata = {n.node0: n.data for n in self._nodeset}
    def __contains__(self, n):
        #print("in Nodes.__contains__",n,n in self._nodeset,self._nodeset)
        return n in self._nodedata or n in self._nodeset
    def __iter__(self):
        for n in self._nodeset:
            yield n
    def __len__(self):
        return len(self._nodeset)
    def __le__(self, other):
        if len(self._nodeset) > len(other):
            return False
        #print("inside Nodes.__le__",other)
        #for n in self._nodeset:
        #    #print("inside Nodes.__le__",n, n in other)
        #    if n not in other:
        #        return False
        #return True
        return all(n in other for n in self._nodeset)
    def __repr__(self):
        return "Nodes({})".format(self._nodeset)
    # Mutation Methods
    def add(self, n, **kwds):
        try:
            {n}  # is n hashable?
        except (TypeError, ValueError):
            n,dd = n
            kwds.update(dd)
        n = asNode(n, **kwds)
        self._nodeset.add(n)
        if n.node0 in self._nodedata:
            self._nodedata[n.node0].update(n.data)
            return False
        self._nodedata[n.node0] = n.data
        return True
    def update(self, nbunch, **kwds):
        for nobj in nbunch:
            self.add(nobj, **kwds)
    def discard(self, n):
        n = asNode(n)
        if self._nodeset.discard(n):
            return self._nodedata.discard(n.node0)
        return False
    # Map-like Methods
    def __getitem__(self, node):
        if isinstance(node, Node):
            return node.data
        return self._nodedata[node]
    def data(self):
        return self._nodedata.items()


# Set | contains, iter, len -> eq/ne/le/lt/gt/ge, and/or/sub/xor, isdisjoint
# MutableSet | add, discard -> remove, clear, pop, iand/ior/isub/ixor
class Edges(MutableSet):
    @classmethod
    def _from_iterable(self, it):
        return set(it)
    def __init__(self, graph, edges):
        self._graph = graph
        self._succ = graph._succ
        self._pred = graph._pred
        self.asedge = graph.asedge
        self.update(self.asedge(obj) for obj in edges)
    def __contains__(self, e):
        u,v = e
        if u not in self._succ:
            return False
        if v not in self._succ[u]:
            return False
        if hasattr(e, "edgekey"):
            return e.edgekey in self._succ[u][v]
        return True
    def __iter__(self):
        for n, nbrs in self._graph._succ.items():
            for nbr, e in nbrs.items():
                yield e
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._graph._succ.items())
    def __repr__(self):
        si = iter(self)
        edrep = [e for _,e in zip(range(3), iter(self))]
        grrep = self._graph.graph.get("name", "graph")
        return "Edges({}, {}...)".format(grrep, edrep)
    # Mutation Methods
    def add(self, e, attr_dict=None, **kwds):
        if attr_dict is None:
            attr_dict = kwds
        else:
            try:
                attr_dict.update(kwds)
            except AttributeError:
                raise NetworkXError("attr_dict must be a dictionary.")
        e = self.asedge(e, **attr_dict)
        u,v = e
        self._add_edge(u, v, e)
    def update(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError("attr_dict must be a dictionary.")
        for e in ebunch:
            e = self.asedge(e, **attr_dict)
            u,v = e
            self._add_edge(u, v, e)
    def _add_edge(self, u, v, e):
        succ = self._graph._succ
        pred = self._graph._pred
        nodes = self._graph.nodes
        u_new = u not in self._succ
        v_new = v not in self._succ
        if u_new:
            succ[u] = {} # fixme factory
            pred[u] = {} # fixme factory
            nodes.add(u)
        if v_new:
            succ[v] = {} # fixme factory
            pred[v] = {} # fixme factory
            nodes.add(v)
        # find the edge
        if not (u_new or v_new):
            if v in succ[u]:
                edge = succ[u][v]
                edge.update(e.data)
                return False
            if (not self._graph._directed) and (v in pred[u]):
                edge = pred[u][v]
                edge.update(e.data)
                return False
        # add new edge
        succ[u][v] = e
        pred[v][u] = e
    def discard(self, e):
        succ = self._graph._succ
        pred = self._graph._pred
        if len(e) == 3:  # MultiEdge
            u,v,k = e
            try:
                del succ[u][v][k]
                del pred[v][u][k]
                if len(succ[u][v]) == 0:
                    del succ[u][v]
                if len(pred[v][u]) == 0:
                    del pred[v][u]
                return True
            except KeyError:
                if self._graph._directed is True:
                    return False
                try:
                    del pred[u][v][k]
                    del succ[v][u][k]
                    if len(pred[u][v]) == 0:
                        del pred[u][v]
                    if len(succ[v][u]) == 0:
                        del succ[v][u]
                    return True
                except KeyError:
                    return False
        # Not MultiEdge
        u,v = e
        try:
            del succ[u][v]
            del pred[v][u]
            if len(succ[u]) == 0:
                del succ[u]
            if len(pred[v]) == 0:
                del pred[v]
            return True
        except KeyError:
            if self.graph._directed is True:
                return False
            try:
                del pred[u][v]
                del succ[v][u]
                if len(pred[u]) == 0:
                    del pred[u]
                if len(succ[v]) == 0:
                    del succ[v]
                return True
            except KeyError:
                return False
    # Map-like Methods
    def __getitem__(self, edge):
        if isinstance(edge, Edge):
            return edge.data
        u,v = edge
        try:
            return self._graph._succ[u][v].data
        except KeyError:
            if self._graph._directed is True:
                raise
            return self._graph._pred[u][v].data
    def data(self):
        return ItemsView(self)



class Graph(object):
    def __init__(self, nodes=None, edges=None, **kwds):
        # adjacency dicts
        self._succ = {}
        self._pred = {}
        # properties
        self._directed = kwds.get("directed", False)
        self._multigraph = kwds.get("multigraph", False)
        # graph attributes
        self.graph = kwds
        # nodes and edges
        if nodes is None:
            nodes = []
        elif edges is None:
            try:
                nodes, edges = nodes.nodes, nodes.edges
            except AttributeError:
                raise NetworkXError("Arguments to Graph() must be a Graph or 2 sets")
        # nodes
        self.nodes = Nodes(self, nodes)
        # edgetype
        if self._directed:
            if self._multigraph:
                self.asedge = asMultiDiEdge
                EdgesClass = MultiDiEdges
            else:
                self.asedge = asDiEdge
                EdgesClass = DiEdges
        else:
            if self._multigraph:
                self.asedge = asMultiEdge
                EdgesClass = MultiEdges
            else:
                self.asedge = asEdge
                EdgesClass = Edges
        # edges
        if edges is None:
            edges = []
        self.edges = EdgesClass(self, edges)
        # Adjacency
        self.su = Adjacency(self._succ)
        self.pr = Adjacency(self._pred)
        self.adj = Adjacency(AtlasUnion(self._succ, self._pred))
        
    @property
    def directed(self):
        return self._directed
    @property
    def multigraph(self):
        return self._multigraph

    def __repr__(self):
        return 'Graph(nodes={}, edges={})'.format(self.nodes, self.edges)
    def clear(self):
        self.graph.clear()
        self.nodes.clear()
    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        return self.__class__(self, directed=self._directed,
                                    multigraph=self.multigraph)
    def size(self, weight=None):
        if weight is None:
            return len(self.edges)
        return sum(wt for keys,wt in self.edges.data(weight))
    def subgraph(self, subnodes):
        subnodes = set(asNode(n) for n in subnodes)
        ed = (e for e in self.edges if e[0] in subnodes\
                                    if e[1] in subnodes)
        return Graph(subnodes, ed, directed=self.directed,
                                   multigraph=self.multigraph)

if __name__ == "__main__":
    # edge
    e = Edge(1,2)
    print e
    u,v = e
    assert u==1 and v==2
    assert asEdge(e) is e
    assert Edge(1,2) == e
    assert Edge(2,1) == e
    e.data['weight']=3
    assert e.data.get('weight',1) == 3
    assert e.data.get('color',1) == 1
    # node
    n = Node(1)
    print n
    assert n.node0 == 1
    n = Node(1, color=2)
    assert n.data['color'] == 2
    assert list(n.data.items()) == [('color', 2)]

    # Nodes
    nodeset = set(asNode(n) for n in range(9))
    nodes = Nodes(Graph(), nodeset)
    nodes2 = Nodes(Graph(), range(9))
    assert nodes == nodes2
    nodes.add(9)
    nodes.add(10,color=2)  # new node with kwds
    nodes.add(9,color=3)  # existing node with kwds
    assert nodes[9] == {'color':3}
    nds = {n:{} for n in range(11)}
    nds[9].update({'color':3})
    nds[10].update({'color':2})
    assert list(nodes.data()) == list(nds.items())

    # Graph
    graph = Graph()
    graph.edges.add((1,2),foo='f',bar='b' )
    graph.edges.add((2,3),foo='f',bar='b' )
    graph.edges.add((3,4),foo='f',bar='b' )
    graph.edges.add((4,5))
    print(graph.nodes)
    assert list(graph.nodes) == list(range(1,6))
    print(graph.nodes.data())
    assert len(graph.nodes) == 5
    assert 1 in graph.nodes
    assert 0 not in graph.nodes
    graph.nodes[1]['a']='b'
    assert graph.nodes[1] == {'a':'b'}
    #
    graph2 = Graph()
    graph2.edges.add((0,1))
    graph2.edges.add((1,2),foo='f',bar='b' )
    graph2.edges.add((2,3))
    graph2.edges.add((3,4))
    try:
        graph2.edges.add((1,2,3))
        print("Incorrectly allowed 3-tuple for simple graph")
    except (Exception, TypeError, ValueError):
        print ("Correctly rejected multiedge for simple graph")
    assert (graph.nodes ^ graph2.nodes) == set([0, 5])
    assert (graph.nodes & graph2.nodes) == set([1,2,3,4])
    #
    print(graph2.edges)
    print(graph2.edges.data())
    assert len(graph2.edges) == 4
    assert list(graph2.edges) == [(0,1), (1,2), (2,3), (3,4)]
    eds = [((0,1),{}), ((1,2),{'foo':'f', 'bar':'b'}), ((2,3),{}), ((3,4),{})]
    assert list(graph2.edges.data()) == eds
    deds = [((0,1),'deft'), ((1,2),'f'), ((2,3),'deft'), ((3,4),'deft')]
    assert [(e,d.get('foo','deft')) for (e,d) in graph2.edges.data()] == deds
    assert (2,3) in graph2.edges
    assert (2,4) not in graph2.edges
    assert (2,10) not in graph2.edges
    assert (10,2) not in graph2.edges
    ans = set([Edge(0,1), Edge(4,5)])
    assert (graph.edges ^ graph2.edges) == ans
    print(graph.edges[(1,2)])

    print("----")

    s = graph.subgraph([1,2])
    print(s)
    print(s.nodes)
    print(s.nodes.data())
    print(s.edges)
    print(s.edges.data())
    print(s.adj)

    print("----")

#    G = Graph(multigraph=True)
#    G.nodes.add(3)
#    G.nodes.update((4, (5,{"color": "red"})))
#    G.edges.add((2,1,0))
#    G.edges.update([(4,6), (7,4,{"weight":2})])
#    print("Nodes:", list(G.nodes))
#    print("Nodes with data:", list(G.nodes.items()))
#    print("Nodes with weight:", list(G.nodes.data("color")))
#    print("Edges:", list(G.e))
#    print("Edges with data:", list(G.edges.data("wt")))
#    print("Degree", list(degree(G)))
#    print("Neighbors of 2:", list(G.a[2]))
#    print("Neighbors of 3:", list(G.a[3]))
#    print("Neighbors of 1:", list(G.a[1]))
#    print("Neighbors of 4:", list(G.a[4]))
#    print("Neighbors with data of 4:", list(G.a[4].values()))
#    print("Directed Graph")
#    DG = Graph(directed=True, multigraph=True)
#    DG.nodes.add(3)
#    G.nodes.update((4, (5,{"color": "red"})))
#    G.edges.add((2,1,0))
#    G.edges.update([(4,6), (7,4,{"weight":2})])
#    print("Nodes:", list(G.nodes))
#    print("Nodes with data:", list(G.nodes.items()))
#    print("Nodes with weight:", list(G.nodes.data("color")))
#    print("Edges:", list(G.e))
#    print("Degree", list(degree(G)))
#    print("InDegree", list(in_degree(G)))
#    print("OutDegree", list(out_degree(G)))
#    print("Neighbors of 2:", list(G.a[2]))
#    print("Neighbors of 3:", list(G.a[3]))
#    print("Neighbors of 1:", list(G.a[1]))
#    print("Neighbors of 4:", list(G.a[4]))
#    print("Neighbors with data of 4:", list(G.a[4].values()))
#    print("Predecessors of 2:", list(G.pr[2]))
#    print("Predecessors of 3:", list(G.pr[3]))
#    print("Predecessors of 1:", list(G.pr[1]))
#    print("Neighbors of 4:", list(G.a[4]))
#    print("Neighbors with data of 4:", list(G.a[4].values()))
#    print("Succcessors of 2:", list(G.pr[2]))
#    print("Succcessors of 3:", list(G.su[3]))
#    print("Succcessors of 1:", list(G.su[1]))
#    print("Neighbors of 4:", list(G.a[4]))
#    print("Neighbors with data of 4:", list(G.a[4].values()))
#    print("END OF INITIAL TESTS")
#
