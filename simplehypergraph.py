from collections import defaultdict, Mapping, Set, ItemsView, MutableSet, MutableMapping

class SimpleHyperGraph(object):
    def __init__(self):
        self.node_data = {}
        self.node_incidence = {}
        self.edge_data = {}
        self.graph = {}
    # Mutating Methods
    def add_node(self, node, **kwds):
        if node in self.node_data:
            self.node_data[node].update(kwds)
            return False
        self.node_data[node] = kwds
        self.node_incidence[node] = set()
        return True
    def add_edge(self, nbunch, **kwds):
        e = frozenset(nbunch)
        if e in self.edge_data:
            self.edge_data[e].update(kwds)
            return False
        self.edge_data[e] = kwds
        for n in e:
            if n not in self.node_data:
                self.node_data[n] = {}
                self.node_incidence[n] = {e}
            else:
                self.node_incidence[n].add(e)
    def remove_edge(self, nbunch):
        e = frozenset(nbunch)
        if e not in self.edge_data:
            raise KeyError(e)
        del self.edge_data[e]
        for n in e:
            self.node_incidence[n].remove(e)
    def remove_node(self, node):
        """Shrink hyperedge by removed node.
        
        Don't delete hyperedge unless only one node left
        (That is, don't make a self-loop if edge has one node left.)
        """
        del self.node_data[node]
        for e in list(self.node_incidence[node]):
            dd = self.edge_data[e]
            self.remove_edge(e)
            newe = e - {node}
            if len(newe) > 1:
                self.add_edge(newe, **dd)
        del self.node_incidence[node]
    # Reporting Methods
    def edges(self, data=False):
        if data is True:
            return self.edge_data.items()
        return self.edge_data.keys()
    def nodes(self, data=False):
        if data is True:
            return self.node_data.items()
        return self.node_data.keys()
    def has_edge(self, nbunch):
        e = frozenset(nbunch)
        return e in self.edge_data
    # report on adjacencies
    def neighbors(self, node):
        for e in self.node_incidence[node]:
            if len(e) == 1:
                yield node
            else:
                for n in e-{node}:
                    yield n
    def adjacency(self):
        for n in self:
            yield n, NeighborMap(self, n)
    def __getitem__(self, node):
        if node in self.node_incidence:
            return NeighborMap(self, node)
        raise KeyError
    # node-container-like behavior
    def __iter__(self):
        return iter(self.node_data)
    def __contains__(self, node):
        return node in self.node_data
    def __len__(self):
        return len(self.node_data)
    # others
    def clear(self):
        self.node_data.clear()
        self.edge_data.clear()
        self.node_incidence.clear()
        self.graph.clear()
    def copy(self):
        G = self.__class__()
        G.nodes.update(self.n)
        G.edges.update(self.e)
        return G
    def order(self):
        return len(self)
    def size(self):
        return len(self.edge_data)

    @property
    def name(self):
        return self.graph.get('name', '')
    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.node_data, self.edge_data)

class NeighborMap(Mapping):
    def __init__(self, graph, node):
        self._graph = graph
        self._node = node
    def __iter__(self):
        node = self._node
        graph = self._graph
        for e in graph.node_incidence[node]:
            if len(e) == 1:
                yield node
            else:
                for nbr in e - {node}:
                    yield nbr
    def __getitem__(self, nbr):
        node = self._node
        graph = self._graph
        return set(e for e in graph.node_incidence[node] if nbr in e)
    def __len__(self):
        return sum(len(e)-1 if len(e)>1 else 1
                   for e in self._graph.node_incidence[self._node])

if __name__ == "__main__":
    G = SimpleHyperGraph()
    G.add_edge((1,2))
    G.add_edge({1,2})
    G.add_node(0, color=0)
    G.add_edge((2,3))
    assert len(G) == 4
    assert G.nodes() - {0,1,2,3} == set()
    assert G.edges() - {frozenset((1,2)),frozenset((2,3))} == set()
    assert set(G[2]) == {1, 3}
    try:
        G.remove_edge((4,3))
        raise Exception("failed to raise KeyError on edge removal",(4,3))
    except KeyError:
        pass
    G.remove_edge((3,2))
    assert set(G[2]) == {1}
    assert G.edges() == {frozenset((1,2))}
    assert set(G.neighbors(1)) == {2}
    G.add_edge((2,3))
    G.remove_node(2)
    assert len(G.edges())==0
    assert len(G) == 3
    G.add_edge({1,2})
    G.add_edge((2,3))
    assert G.has_edge((1,2))
    adj = dict(G.adjacency())
    assert adj[1].keys() - {2} == set()
    #print(list(adj[1].items()))
    assert repr(list(adj[1].items())) == "[(2, {frozenset({1, 2})})]"
    assert set(G) == {0,1,2,3}
    assert 3 in G and 0 in G and 5 not in G
    assert G.size() == 2
    assert G.order() == 4
    #print(G)
    assert repr(G) == ("SimpleHyperGraph("
                   "{0: {'color': 0}, 1: {}, 2: {}, 3: {}}, "
                   "{frozenset({1, 2}): {}, frozenset({2, 3}): {}})")





