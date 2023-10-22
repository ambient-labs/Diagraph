from ..utils.depends import Depends
from .diagraph import Diagraph
from .diagraph_node_group import DiagraphNodeGroup


def describe_diagraph_node_group():
    def test_it_instantiates():
        DiagraphNodeGroup(Diagraph())

    def test_it_iterates_through_nodes():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return "d1"

        def d2(d0: str = Depends(d0)):
            return "d2"

        for node in Diagraph(d1, d2)[1]:
            assert node.key in [d1, d2]

    def test_it_can_index_into_a_node():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return "d1"

        def d2(d0: str = Depends(d0)):
            return "d2"

        diagraph = Diagraph(d1, d2)
        assert diagraph[1][0].key == d1
        assert diagraph[1][1].key == d2

    def test_it_can_return_len():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return "d1"

        def d2(d0: str = Depends(d0)):
            return "d2"

        diagraph = Diagraph(d1, d2)
        assert len(diagraph[0]) == 1
        assert len(diagraph[1]) == 2

    def test_it_can_return_in():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return "d1"

        def d2(d0: str = Depends(d0)):
            return "d2"

        layer = Diagraph(d1, d2)[1]
        assert d0 not in layer
        assert d1 in layer
        assert d2 in layer

    def test_it_can_return_results():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return "d1"

        def d2(d0: str = Depends(d0)):
            return "d2"

        diagraph = Diagraph(d1, d2).run()
        assert diagraph[0].result == "d0"
        assert diagraph[1].result == ("d1", "d2")

    def test_it_can_set_results():
        def d0():
            return "d0"

        def d1(d0: str = Depends(d0)):
            return f"{d0} d1"

        def d2(d0: str = Depends(d0)):
            return f"{d0} d2"

        diagraph = Diagraph(d1, d2).run()
        assert diagraph.result == ("d0 d1", "d0 d2")
        diagraph[0].result = "foo"
        diagraph[1].run()
        assert diagraph.result == ("foo d1", "foo d2")
        diagraph[1].result = ("bar", "baz")
        assert diagraph[0].result == "foo"
        assert diagraph[1].result == ("bar", "baz")
        assert diagraph.result == ("bar", "baz")
