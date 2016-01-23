# This file was derived from networkx/classes/graph.py
# which is
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from __future__ import division
from copy import deepcopy

import networkx as nx
from networkx.exception import NetworkXError

from graph import Graph

class nxGraph(Graph):
    def __init__(self, data=None, **attr):
        super(nxGraph, self).__init__(data=data, **attr)
        self.graph = self.data    # dictionary for graph attributes
        self.node = self._nodedata   # empty node attribute dict
        self.adj = self._adjacency   # empty adjacency dict
        # DEPRECATE
        self.edge = self.adj



    # keep these existing methods?
    @property
    def name(self):
        return self.data.get('name', '')
    @name.setter
    def name(self, s):
        self.data['name'] = s
    def __str__(self):
        return self.name


    # deprecate? - replace with for n in Graph.nodes?
    def __contains__(self, n):
        try:
            return n in self.n
        except TypeError:
            return False

    # deprecate --  replace with graph.a[n] or graph.e[n]
    def __getitem__(self, n):
        return self.a[n]

    # deprecate - use G.n.add()
    def add_node(self, n, attr_dict=None, **attr):
        self.n.add(n, attr_dict=attr_dict, **attr)

    # deprecate - use G.n.update()
    def add_nodes_from(self, nodes, **attr):
        self.n.update(nodes, **attr)

    # deprecate - use G.n.remove(n)
    def remove_node(self,n):
        self.n.remove(n)

    # deprecate
    def remove_nodes_from(self,nodes):
        self.n.difference_update(nodes)

    # deprecate - use G.n, G.n.items(), G.n.data()
    # note that there is no specification in new interface for
    # data=attr or default
    # could put it in as
    # graph.n.items(attr=None, default=None)
    # graph.n.data(attr=None, default=None)
    def nodes(self, data=False, default=None):
        if data is True:
            return self.n.items()
        elif data is not False:
            return ((n,d.get(data,default)) for n,d in self.n.items())
        else:
            return iter(self.n)
    # deprecate - use n in self.n
    def has_node(self, n):
        try:
            return n in self.n
        except TypeError:
            return False

    # deprecate - use G.edge.add()
    def add_edge(self, u, v, attr_dict=None, **attr):
        self.e.add(u, v, attr_dict=attr_dict, **attr)

    # FIXME rewrite in terms of new interface
    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        self.e.update(ebunch, attr_dict=attr_dict, **attr)

    # FIXME rewrite in terms of new interface
    def add_weighted_edges_from(self, ebunch, weight='weight', **attr):
        self.e.update(((u, v, {weight: d}) for u, v, d in ebunch), **attr)

    # deprecate  use G.e, G.e.items(), G.e.data()
    # no interface for data=attr, default=  but could make one
    # change semantics for edges(nbunch) to G.s(nbunch).e?
    # that is, return only edges between those in nbunch and not all
    # edges adjecent to nbunch?
    def edges(self, nbunch=None, data=False, default=None):
        if nbunch is None:
            if data is True:
                return ((u,v,d) for (u,v),d in self.e.items())
            elif data is not False:
                return ((u,v,d.get(data,default)) for (u,v),d in self.e.items())
            else:  # data is False
                return self.e
        else:
            bunch = set(self._nbunch_iter(nbunch))
            if data is True:
                return ((u,v,d) for (u,v),d in self.e.items() if u in bunch or v in bunch)
            elif data is not False:
                return ((u,v,d.get(data,default)) for (u,v),d in self.e.items() if u in bunch or v in bunch)
            else:  # data is False
                return ((u,v) for u,v in self.e if u in bunch or v in bunch)

    # fixme, deprecate for self.a[n]?
    def neighbors(self, n):
        try:
            return iter(self.a[n])
        except KeyError:
            raise NetworkXError("The node %s is not in the graph." % (n,))


    # deprecate - use G.n.degree(), G.s(nbunch).degree
    # what do we do about singleton?
    # singleton degree implementation is ugly here
    def degree(self, nbunch=None, weight=None):
        if nbunch in self:
            print "here"
            (n,d) = next(self.n.degree(weight=weight))
            return d
        if nbunch is None:
            return self.n.degree(weight=weight)
        else:
            return ((n,d) for (n,d) in self.n.degree(weight=weight) if n in nbunch)




    # FIXME deprecate - use G.e.remove()
    def remove_edge(self, u, v):
        self.e.remove(u,v)

    # FIXME rewrite in terms of new interface
    def remove_edges_from(self, ebunch):
        for e in ebunch:
            u,v = e[:2]
            try:
                self.e.remove(u,v)
            except NetworkXError: # shouldn't silently error here
                pass


    # deprecate - use (u,v) in self.e
    def has_edge(self, u, v):
        return (u,v) in self.e

    # deprecate - use G.a
    def adjacency(self):
        return iter(self.a)

    # deprecate - use G.e[(u,v)], no default= keyword
    def get_edge_data(self, u, v, default=None):
        try:
            return self.e[(u,v)]
        except KeyError:
            return default

    # deprecate
    def nodes_with_selfloops(self):
        return self.n.selfloops()

    # deprecate but consider better interface?
    def selfloop_edges(self, data=False, default=None):
        if data is True:
            return ((n,n,self.e[(n,n)]) for n,n in self.e.selfloops())
        elif data is not False:
            return ((n,n,self.e[(n,n)].get(data,default)) for n,n in self.e.selfloops())
        else:
            return self.e.selfloops()

    # deprecate, use len(G.e.selfloops())
    def number_of_selfloops(self):
        return sum(1 for _ in self.e.selfloops())

    # modify to # copy=True (old behavior) # copy=False (view)
    def subgraph(self, nbunch, copy=True):
        s = self.s(nbunch) # view
        if copy:
            # create new graph and copy subgraph into it
            H = self.__class__()
            # copy node and attribute dictionaries
            for n,_ in s.a:
                H._nodedata[n] = self._nodedata[n]
            # namespace shortcuts for speed
            H_adj = H.adj
            self_adj = s.a
            # add nodes and edges (undirected method)
            for n,_ in s.a:
                Hnbrs = {}
                H_adj[n] = Hnbrs
                for nbr, d in self_adj[n].items():
                    if nbr in H_adj:
                        # add both representations of edge: n-nbr and nbr-n
                        Hnbrs[nbr] = d
                        H_adj[nbr][n] = d
            H.graph = self.data
        else:
            H = s
        return H

    # completely deprecated functions
    def add_star(self, nodes, **attr):
        nlist = list(nodes)
        v = nlist[0]
        edges = ((v, n) for n in nlist[1:])
        self.add_edges_from(edges, **attr)

    def add_path(self, nodes, **attr):
        nlist = list(nodes)
        edges = zip(nlist[:-1], nlist[1:])
        self.add_edges_from(edges, **attr)

    def add_cycle(self, nodes, **attr):
        nlist = list(nodes)
        edges = zip(nlist, nlist[1:] + [nlist[0]])
        self.add_edges_from(edges, **attr)

    def nbunch_iter(self, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(self.adj)
        elif nbunch in self:  # if nbunch is a single node
            bunch = iter([nbunch])
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist, adj):
                try:
                    for n in nlist:
                        if n in adj:
                            yield n
                except TypeError as e:
                    message = e.args[0]
                    # capture error for non-sequence/iterator nbunch.
                    if 'iter' in message:
                        raise NetworkXError(
                            "nbunch is not a node or a sequence of nodes.")
                    # capture error for unhashable node.
                    elif 'hashable' in message:
                        raise NetworkXError(
                            "Node {} in the sequence nbunch is not a valid node.".format(n))
                    else:
                        raise
            bunch = bunch_iter(nbunch, self.adj)
        return bunch
