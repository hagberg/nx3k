from collections import MappingView, Set, ValuesView, ItemsView
from networkx.exception import NetworkXError

# =================
#  EdgeView Classes
# =================
#  Cheap, quick, lightweight access to:
#    - edge keys (iterate, len, contains) [could do set ops here)
#    - edge data (iterate, len, contains--but maybe don't need contains?)
#    - edge items (iterate, len, contains)
#
#  Set Operations Broken on data/items
#    Unlike dictViews, the data and items here always have dicts in them
#    so we can't easily do set operations.  Perhaps we can do set operations
#    on the keys portion of items and then hang the dicts off. Not sure 
#    it makes sense to do sets with dataview.  
#    Maybe we don't need dataview at all?
#    The KeysView methods simply call th Edges methods, so maybe dont need
#    that either.
#
class BaseEdgeView(object):
    __slots__ = ["_edges"]
    def __init__(self, edges):
        self._edges = edges
    def __repr__(self):
        return '{0.__class__.__name__}({0._edges!r})'.format(self)
    def __len__(self):
        # size of graph
        return len(self._edges)

class EdgeKeys(BaseEdgeView):
    __slots__ = ["_edges"]
    def __iter__(self):
        return iter(self._edges)
    def __contains__(self, key):
        return key in self._edges

#class EdgeData(BaseEdgeView):
#    __slots__ = ["_edges"]
#    def __iter__(self):
#        for e,d in self._edges._items():
#            yield d
#    def __contains__(self, data):
#        # Do we need/want to provide ability to look up a datadict?
#        # Maybe leave this out?
#        # need to look at all data
#        return any(d == data for d in self)

class EdgeData(ValuesView):
    pass
class EdgeItems(ItemsView):
    pass

#class EdgeItems(BaseEdgeView):
#    __slots__ = ["_edges"]
#    def __iter__(self):
#        return self._edges._items()
#    def __contains__(self, item):
#        try:
#            (u,v),d = item # raises for ``eitem`` not ((u,v),d)
#            ddict = self._edges[(u,v)]
#            return d == ddict
#        except:
#            return False


class Edges(Set):
    """ Directed or Undirected Edges class.
    
        The two adjacency structures _succ and _pred are split.
        The order provided on initial addition is the orientation of 
        storage even for undirected edges.

        ``directed`` is a read-only property. 
        Behavior of methods is affected by the directed property in
        __contains__, __getitem__, add, update, remove, discard
    """
    __slots__ = ('_node', '_succ', '_pred', '_directed')
    def __init__(self, node, succ, pred, directed):
        self._node = node
        self._succ = succ
        self._pred = pred
        self._directed = directed

    @property
    def directed(self):
        return self._directed

    @classmethod
    def _from_iterable(cls, it):
        '''Adapted from Set class to return a set instead of Edges'''
        return set(it)

    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self,list(self))
    def keys(self):
        return EdgeKeys(self)
    def data(self):
        return EdgeData(self)
    def items(self):
        return EdgeItems(self)
    def selfloops(self):
        return ((n, n) for n, nbrs in self._succ.items() if n in nbrs)

    def __len__(self):
        """size of graph"""
        return sum(len(nbrs) for n, nbrs in self._succ.items())
    def __iter__(self):
        nodes_nbrs = self._succ.items()
        for n, nbrs in nodes_nbrs:
            for nbr in nbrs:
                yield (n, nbr)
    def _items(self):
        # Helper Function for Views and Adjacency
        nodes_nbrs = self._succ.items()
        for n, nbrs in nodes_nbrs:
            for nbr, ddict in nbrs.items():
                yield (n,nbr),ddict
    # Affected by self.directed
    def __contains__(self, key):
        try:
            u,v = key
            if v in self._succ[u]:
                return True
            # if not directed check other direction
            return (not self.directed) and (v in self._pred[u])
        except:
            return False
    def __getitem__(self, key):
        try:
            u,v = key
        except TypeError:
            raise NetworkXError('bad edge key: use edge key = (u,v)')
        try:
            return self._succ[u][v]
        except KeyError:
            if self.directed:
                raise
            return self._pred[u][v]
    # Mutating Methods
    def add(self, u, v, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        u_new = u not in self._succ
        v_new = v not in self._succ
        if u_new:
            self._succ[u] = {} # fixme factory
            self._pred[u] = {} # fixme factory
            self._node[u] = {}
        if v_new:
            self._succ[v] = {} # fixme factory
            self._pred[v] = {} # fixme factory
            self._node[v] = {}
        # find the edge
        if not (u_new or v_new):
            if v in self._succ[u]:
                datadict = self._succ[u][v]
                datadict.update(attr_dict)
                return False # not new edge
            # if not directed check other direction
            if (not self.directed) and v in self._pred[u]:
                datadict = self._pred[u][v]
                datadict.update(attr_dict)
                return False # not new edge
            # else new edge-- drop out of if
        # add new edge
        datadict = {}
        datadict.update(attr_dict)
        self._succ[u][v] = datadict
        self._pred[v][u] = datadict
        return True # new edge


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
                except TypeError as e:
                    dd = v
                    u,v = u
                else:
                    dd = {}  # doesnt need edge_attr_dict_factory
            else:
                msg = "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,)
                raise NetworkXError(msg)
            # add nodes
            u_new = u not in self._succ
            v_new = v not in self._succ
            if u_new:
                self._succ[u] = {} # fixme factory
                self._pred[u] = {} # fixme factory
                self._node[u] = {}
            if v_new:
                self._succ[v] = {} # fixme factory
                self._pred[v] = {} # fixme factory
                self._node[v] = {}
            # find the edge
            if not (u_new or v_new):
                if v in self._succ[u]:
                    datadict = self._succ[u][v]
                    datadict.update(attr_dict)
                    datadict.update(dd)
                    continue
                # if not directed check other direction
                if (not self.directed) and v in self._pred[u]:
                    datadict = self._pred[u][v]
                    datadict.update(attr_dict)
                    datadict.update(dd)
                    continue
                # else new edge-- drop out of if
            # add new edge
            datadict = {}
            datadict.update(attr_dict)
            datadict.update(dd)
            self._succ[u][v] = datadict
            self._pred[v][u] = datadict
    def discard(self, u, v):
        try:
            del self._succ[u][v]
            del self._pred[v][u]
            return True
        except KeyError:
            return False
    def remove(self, u, v):
        try:
            del self._succ[u][v]
        except KeyError:
            raise NetworkXError("The edge %s-%s is not in the graph" % (u, v))
        try:
            del self._pred[v][u]
        except KeyError: # self-loop can cause failure in undirected
            pass
    def clear(self):
        for n in self._succ:
            self._succ[n].clear()
            self._pred[n].clear()
