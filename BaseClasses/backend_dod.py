from __future__ import division
from abstract_classes import ABCGraphData

#ABCGraphData | add_node, remove_node, add_edge, remove_edge
# nodes_iter, edges_iter, nodes_data, edges_data, get_edge_data
# get_node_data, successors_iter, predecessors_iter, neighbors_iter
# successors_data, predecessors_data, neighbors_data,
# in_degree, out_degree, degree, order
#  -> size, clear, clear_edges
class DodGraphData(ABCGraphData):
    def __init__(self, directed, multigraph):
        self._nodes = {}
        self._succ = {}
        self._pred = {}
        self._directed = directed
        self._multigraph = multigraph
    def add_node(self, node, dd):
        if node in self._nodes:
            self._nodes[node].update(dd)
            return False
        self._nodes[node] = nn = {}
        nn.update(dd)
        self._succ[node] = {}
        self._pred[node] = {}
        return True
    def remove_node(self, node):
        del self._nodes[node]
        for nbr in self._succ[node]:
            del self._pred[nbr][node]
        for nbr in self._pred[node]:
            del self._succ[nbr][node]
        del self._succ[node]
        del self._pred[node]
    def add_edge(self, ekeys, dd):
        u,v = ekeys
        succ = self._succ
        pred = self._pred
        nodes = self._nodes
        # add nodes
        u_new = u not in self._succ
        v_new = v not in self._succ
        if u_new:
            nodes[u] = {}
            succ[u] = {}
            pred[u] = {}
        if v_new:
            nodes[v] = {}
            succ[v] = {}
            pred[v] = {}
        # find edge
        if not (u_new or v_new):
            if v in succ[u]:
                succ[u][v].update(dd)
                return False
            if (not self._directed) and (v in pred[u]):
                pred[u][v].update(dd)
                return False
        # new edge
        succ[u][v] = dd
        pred[v][u] = dd
        return True
    def remove_edge(self, ekeys):
        u,v = ekeys
        try:
            del self._succ[u][v]
            del self._pred[v][u]
            return True
        except KeyError:
            return False
    # Reporting methods
    def edges_iter(self):
        for n,nbrs in self._succ.items():
            for nbr in nbrs:
                yield n,nbr
    def edges_data(self, weight_func=None):
        if weight_func is None:
            weight_func = lambda x:x
        for n,nbrs in self._succ.items():
            for nbr,dd in nbrs.items():
                yield n,nbr,weight_func(dd)
    def nodes_iter(self):
        return iter(self._nodes)
    def nodes_data(self, weight_func=None):
        if weight_func is None:
            weight_func = lambda x:x
        for n,dd in self._nodes.items():
            yield n,weight_func(dd)
    def get_edge_data(self, ekeys, weight_func):
        u,v = ekeys
        return weight_func(self._succ[u][v])
    def get_node_data(self, node, weight_func):
        return weight_func(self._nodes[node])
    def neighbors_iter(self, node):
        for nbr in self._succ[node]:
            yield nbr
        for nbr in self._pred[node]:
            if nbr != node:
                yield nbr
    def neighbors_data(self, node):
        for nbr,dd in self._succ[node].items():
            yield nbr,dd
        for nbr,dd in self._pred[node].items():
            if nbr != node:
                yield nbr,dd
    def successors_iter(self, node):
        for nbr in self._succ[node]:
            yield nbr
        if not self._directed:
            for nbr in self._pred[node]:
                if nbr != node:
                    yield nbr
    def successors_data(self, node):
        for nbr,dd in self._succ[node].items():
            yield nbr,dd
        if not self._directed:
            for nbr,dd in self._pred[node].items():
                if nbr != node:
                    yield nbr,dd
    def predecessors_iter(self, _node):
        for nbrd in self._pred[_node]:
            yield nbr
        if not self._directed:
            for nbr in self._succ[node]:
                if nbr != node:
                    yield nbr
    def predecessors_data(self, _node):
        for nbr,dd in self._pred[_node].items():
            yield nbr,dd
        if not self._directed:
            for nbr,dd in self._succ[node].items():
                if nbr != node:
                    yield nbr,dd
    def out_degree(self, node):
        if self._directed:
            return len(self._succ[node])
        return (len(self._succ[node]) + len(self._pred[node]))/2
    def in_degree(self, node):
        if self._directed:
            return len(self._pred[node])
        return (len(self._succ[node]) + len(self._pred[node]))/2
    def degree(self, node):
        return len(self._succ[node]) + len(self._pred[node])
    def order(self):
        return len(self._nodes)

