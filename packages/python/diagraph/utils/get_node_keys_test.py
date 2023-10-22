from ..classes.diagraph import Diagraph
from .depends import Depends
from .get_node_keys import get_node_keys


def describe_get_node_keys():
    def test_it_returns_keys():
        def foo():
            pass

        assert get_node_keys([foo]) == [foo]

    def test_it_returns_keys_for_diagraph_node_group():
        def a():
            return "a"

        def b(a=Depends(a)):
            return "b"

        def c(a=Depends(a)):
            return "c"

        dg = Diagraph(b, c)
        group = dg[-1]
        print(group)
        assert get_node_keys(group) == [b, c]
