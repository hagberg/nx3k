from __future__ import division
from abstract_classes import ABCGraphData

#ABCGraphData | add_node, remove_node, add_edge, remove_edge
# nodes_iter, edges_iter, nodes_data, edges_data, get_edge_data
# get_node_data, successors_iter, predecessors_iter, neighbors_iter
# successors_data, predecessors_data, neighbors_data,
# in_degree, out_degree, degree, order
#  -> size, clear, clear_edges
class NXGraphData(ABCGraphData):
    def __init__(self, directed, multigraph):
        self._directed = directed
        if directed is True:
            self._nxgraph = nx.DiGraph()
        else:
            self._nxgraph = nx.Graph()
        self._multigraph = multigraph
        assert multigraph is False
    def add_node(self, node, dd):
        self._nxgraph.add_node(node, **dd)
    def remove_node(self, node):
        self._nxgraph.remove_node(node)
    def add_edge(self, ekeys, dd):
        u,v = ekeys
        self._nxgraph.add_edge(u, v, **dd)
    def remove_edge(self, ekeys):
        u,v = ekeys
        self._nxgraph.remove_edge(u, v)
    # Reporting methods
    def edges_iter(self):
        return self._nxgraph.edges()
    def edges_data(self, weight_func=None):
        return self._nxgraph.edges(data=weight_func)
    def nodes_iter(self):
        return self._nxgraph.nodes()
    def nodes_data(self, weight_func=None):
        return self._nxgraph.nodes(data=weight_func)
    def get_edge_data(self, ekeys, weight_func):
        u,v = ekeys
        return weight_func(self._nxgraph.adj[u][v])
    def get_node_data(self, node, weight_func):
        return weight_func(self._nxgraph.node[node])
    def neighbors_iter(self, node):
        return self._nxgraph.neighbors(node)
    def neighbors_data(self, node):
        if self._directed:
            for nbr,dd in self._nxgraph.succ[node].items():
                yield nbr,dd
            for nbr,dd in self._nxgraph.pred[node].items():
                if nbr != node:
                    yield nbr,dd
        else:
            for nbr,dd in self._nxgraph.adj[node].items():
                yield nbr,dd
    def successors_iter(self, node):
        return self._nxgraph.successors(node)
    def successors_data(self, node):
        if self._directed:
            for nbr,dd in self._nxgraph.succ[node].items():
                yield nbr,dd
        else:
            for nbr,dd in self._nxgraph.adj[node].items():
                yield nbr,dd
    def predecessors_iter(self, _node):
        return self._nxgraph.predecessors(node)
    def predecessors_data(self, _node):
        if self._directed:
            for nbr,dd in self._nxgraph.pred[node].items():
                yield nbr,dd
        else:
            for nbr,dd in self._nxgraph.adj[node].items():
                yield nbr,dd
    def out_degree(self, node):
        if self._directed:
            return len(self._nxgraph.succ[node])
        return len(self._nxgraph.adj[node]) // 2
    def in_degree(self, node):
        if self._directed:
            return len(self._nxgraph.pred[node])
        return len(self._nxgraph.adj[node]) // 2
    def degree(self, node):
        if self._directed:
            return len(self._nxgraph.succ[node]) + len(self._nxgraph.pred[node])
        return len(self._nxgraph.adj[node]) // 2
    def order(self):
        return len(self._nxgraph.node)

