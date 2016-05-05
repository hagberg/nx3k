#
#   TESTS
#
from nose.tools import assert_true, assert_equal, assert_raises

from edges import Edges, EdgeKeys, EdgeData, EdgeItems

class BaseEdgeTests(object):
    def setup_edges(self):
        self.edlist = [{1:"one"}, {1:"two"}, {1:"three"}, {1:"four"}]
        ed1, ed2, ed3, ed4 = self.edlist
        Ge = self.Ge
        Ge.add(0,1,ed1)
        Ge.add(0,0,ed2)
        Ge.update([(1,0,ed3), (2,3,ed4)])
    def test_iter_items(self):
        Ge = self.Ge
        ed1, ed2, ed3, ed4 = self.edlist
        if Ge.directed:
            ans = [(0,1), (0,0), (1,0), (2,3)]
        else:
            ans = [(0,1), (0,0), (2,3)]
        assert_equal( sorted(Ge), sorted(ans))
        if Ge.directed:
            ans = [((0,1),ed1), ((0,0),ed2), ((1,0),ed3), ((2,3),ed4)]
        else:
            ans = [((0,1),ed3), ((0,0),ed2), ((2,3),ed4)]
        assert_equal( sorted(Ge._items()), sorted(ans))
    def test_view_data_keys(self):
        Ge = self.Ge
        ed1, ed2, ed3, ed4 = self.edlist
        if Ge.directed:
            ans = [((0,1),ed1), ((0,0),ed2), ((1,0),ed3), ((2,3),ed4)]
        else:
            ans = [((0,1),ed3), ((0,0),ed2), ((2,3),ed4)]
        # iter
        assert_equal( sorted(Ge.items()), sorted(ans))
        assert_equal( sorted(Ge.data()), sorted(d for k,d in ans))
        assert_equal( sorted(Ge.keys()), sorted(k for k,d in ans))
        # contains
        assert_true( (0,1) in Ge.keys() )
        assert_true( (0,3) not in Ge.keys() )
        assert_true( (0,8) not in Ge.keys() )

        extras = [((0,1),{1:"none"}), ((2,3),ed4), ((0,8),ed3)]
        assert_true( ed2 in Ge.data() )
        assert_true( extras[0][1] not in Ge.data() )
        assert_true( ((0,0),ed2) in Ge.items() )
        assert_true( extras[0] not in Ge.items() )
        assert_true( extras[1] in Ge.items() )
        assert_true( extras[2] not in Ge.items() )


    def test_len(self):
        Ge = self.Ge
        assert_equal(len(Ge), 4 if Ge.directed else 3)
        assert_equal(len(Ge.items()), len(Ge))
        assert_equal(len(Ge.data()), len(Ge))
        assert_equal(len(Ge.keys()), len(Ge))

    def test_contains_get(self):
        Ge = self.Ge
        ed1, ed2, ed3, ed4 = self.edlist
        assert_true((0,1) in Ge)
        assert_true((1,0) in Ge)
        assert_true((2,3) in Ge)
        assert_true((0,0) in Ge)
        if Ge.directed:
            assert_true((3,2) not in Ge)
        else:
            assert_true((3,2) in Ge)
        assert_true((4, 5) not in Ge)
        assert_true((4, 4) not in Ge)
        # getitem
        assert_true(Ge[(0,1)] == (ed1 if Ge.directed else ed3))
        assert_true(Ge[(1,0)] == ed3)
        assert_true(Ge[(2,3)] == ed4)
        assert_true(Ge[(0,0)] == ed2)

    def test_remove_clear(self):
        Ge = self.Ge
        Ge.remove(0,1)
        assert_true((0,1) not in Ge)
        if Ge.directed:
            assert_true((1,0) in Ge)
        else:
            assert_true((1,0) not in Ge)
        Ge.clear()
        assert_equal(len(Ge._node), 5)
        assert_equal(len(Ge), 0)

    def test_set_ops(self):
        Ge = self.Ge
        extras = [(1,2), (0,1), (3,4)]
        if Ge.directed:
            edgs = [(0,1), (0,0), (1,0), (2,3)]
        else:
            edgs = [(0,1), (0,0), (2,3)]
        assert_equal(Ge | extras, set(edgs) | set(extras) )
        assert_equal(Ge & extras, set(edgs) & set(extras) )
        assert_equal(Ge ^ extras, set(edgs) ^ set(extras) )
        assert_equal(Ge - extras, set(edgs) - set(extras) )
        assert_equal(extras - Ge, set(extras) - set(edgs) )

class TestDiEdges(BaseEdgeTests):
    def setUp(self):
        node ={4:{}}
        succ = {}
        pred = {}
        self.Ge = Edges(node, succ, pred, directed=True)
        self.setup_edges()
class TestUndiEdges(BaseEdgeTests):
    def setUp(self):
        node ={4:{}}
        succ = {}
        pred = {}
        self.Ge = Edges(node, succ, pred, directed=False)
        self.setup_edges()
        self.setup_edges()


