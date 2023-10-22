from collections.abc import Callable
from inspect import getsource as _getsource
from textwrap import dedent

import pytest

from ..decorators import prompt as _prompt
from ..utils.depends import Depends
from . import diagraph as _diagraph
from .diagraph import Diagraph
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup


@pytest.fixture(autouse=True)
def _clear_defaults(request):
    _prompt.__default_llm__ = None
    _diagraph.global_log_fn = None
    _diagraph.global_error_fn = None
    yield
    _prompt.__default_llm__ = None
    _diagraph.global_log_fn = None
    _diagraph.global_error_fn = None


def getsource(fn: Callable):
    return dedent(_getsource(fn)).strip()


def describe_instantiation():
    def test_it_instantiates_empty_diagraph():
        Diagraph()

    def test_it_instantiates_a_single_item_diagraph():
        def foo():
            return "foo"

        Diagraph(foo)


def describe_nodes():
    def test_it_gets_back_a_node_wrapper_for_a_function():
        def foo():
            return "foo"

        dg = Diagraph(foo, use_string_keys=False)

        node = dg[foo]
        assert isinstance(node, DiagraphNode)
        assert node.fn == foo

    def describe_string_keys():
        def test_it_gets_back_a_node_wrapper_for_a_function_using_string_keys():
            def foo():
                return "foo"

            dg = Diagraph(foo, use_string_keys=True, node_dict={"foo": foo})

            node = dg["foo"]
            assert isinstance(node, DiagraphNode)
            assert node.fn == foo

        def test_it_can_run_from_a_string_key():
            def foo():
                return "foo"

            dg = Diagraph(foo, use_string_keys=True, node_dict={"foo": foo})

            dg.run("foo")
            assert dg.result == "foo"

        def test_nodes_can_specify_dependencies_as_strings_alongside_string_keys():
            def foo():
                return "foo"

            def bar(foo=Depends("foo")):
                return f"bar: {foo}"

            def baz(bar=Depends("bar")):
                return f"baz: {bar}"

            dg = Diagraph(
                baz,
                use_string_keys=True,
                node_dict={"foo": foo, "bar": bar, "baz": baz},
            )
            dg["foo"].result = "foo1"

            dg["bar"].run()
            assert dg.result == "baz: bar: foo1"


def describe_indexing():
    def test_it_gets_back_a_node_wrapper_for_an_index():
        def foo():
            return "foo"

        def bar(foo: str = Depends(foo)):
            return "bar"

        def baz(bar: str = Depends(bar)):
            return "baz"

        diagraph = Diagraph(baz)

        assert isinstance(diagraph[0], DiagraphNodeGroup)
        assert diagraph[0][0].fn == foo
        assert isinstance(diagraph[2], DiagraphNodeGroup)
        assert diagraph[2][0].fn == baz
        assert isinstance(diagraph[-1], DiagraphNodeGroup)
        assert diagraph[-1][0].fn == baz

    def test_it_gets_back_a_tuple_for_parallels():
        def l0():
            return "foo"

        def l1_l(l0: str = Depends(l0)):
            return "bar"

        def l1_r(l0: str = Depends(l0)):
            return "baz"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return "qux"

        diagraph = Diagraph(l2)

        def check_tuple(key):
            nodes = diagraph[key]
            assert isinstance(nodes, DiagraphNodeGroup)
            assert len(nodes) == 2
            return set([n.fn for n in nodes])

        assert check_tuple(1) == {l1_l, l1_r}
        assert check_tuple(-2) == {l1_l, l1_r}

    def test_it_gets_back_a_tuple_for_parallels_by_specifying_either_node_as_key():
        def l0():
            return "foo"

        def l1_l(l0: str = Depends(l0)):
            return "bar"

        def l1_r(l0: str = Depends(l0)):
            return "baz"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return "qux"

        diagraph = Diagraph(l2)

        assert diagraph[l1_l].fn == l1_l
        assert diagraph[l1_r].fn == l1_r

    def test_a_complicated_tree():
        def l0():
            pass

        def l1_l(l0: str = Depends(l0)):
            pass

        def l1_r(l0: str = Depends(l0)):
            pass

        def l2_l(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            pass

        def l2_r(l1_r: str = Depends(l1_r)):
            pass

        def l3_l(
            l2_l: str = Depends(l2_l),
            l1_r: str = Depends(l1_r),
            l0: str = Depends(l0),
        ):
            pass

        def l4(
            l3_l: str = Depends(l3_l),
            l1_r: str = Depends(l1_r),
            l2_r: str = Depends(l2_r),
        ):
            pass

        diagraph = Diagraph(l4)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l2_r, l3_l, l4]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (4, (l4,)),
            (-5, (l0,)),
            (-4, (l1_l, l1_r)),
            (-3, (l2_l, l2_r)),
            (-2, (l3_l,)),
            (-1, (l4,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_a_complicated_tree_with_multiple_terminal_points():
        def l0():
            pass

        def l1_l(l0: str = Depends(l0)):
            pass

        def l1_r(l0: str = Depends(l0)):
            pass

        def l2_l(l1_l: str = Depends(l1_l)):
            pass

        def l2_r(l1_r: str = Depends(l1_r)):
            pass

        def l3_l(l2_l: str = Depends(l2_l), l1_r: str = Depends(l1_r)):
            pass

        diagraph = Diagraph(l3_l, l2_r)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l3_l, l2_r]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (-4, (l0,)),
            (-3, (l1_l, l1_r)),
            (-2, (l2_l, l2_r)),
            (-1, (l3_l,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_a_complicated_tree_with_multiple_origin_points():
        def l0_l():
            pass

        def l0_r():
            pass

        def l1_l(l0_l: str = Depends(l0_l)):
            pass

        def l1_r(l0_r: str = Depends(l0_r)):
            pass

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            pass

        diagraph = Diagraph(l2)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0_l, l0_r, l1_l, l1_r, l2]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0_l, l0_r)),
            (1, (l1_l, l1_r)),
            (2, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

        for index, nodes in [
            (-3, (l0_l, l0_r)),
            (-2, (l1_l, l1_r)),
            (-1, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_it_can_index_into_a_triangle():
        def d0():
            pass

        def d1a(d0: str = Depends(d0)):
            pass

        def d1b(d0: str = Depends(d0)):
            pass

        diagraph = Diagraph(d1a, d1b)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0, d1a, d1b]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (d0,),
            ),
            (
                1,
                (
                    d1a,
                    d1b,
                ),
            ),
            (
                -2,
                (d0,),
            ),
            (
                -1,
                (
                    d1a,
                    d1b,
                ),
            ),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer

    def test_it_can_index_into_a_reverse_triangle():
        def d0a():
            pass

        def d0b():
            pass

        def d1(d0a: str = Depends(d0a), db0: str = Depends(d0b)):
            pass

        diagraph = Diagraph(d1)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0a, d0b, d1]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (
                    d0a,
                    d0b,
                ),
            ),
            (1, (d1,)),
            (
                -2,
                (
                    d0a,
                    d0b,
                ),
            ),
            (-1, (d1,)),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer

    def test_it_can_index_into_a_deep_reverse_triangle():
        def d0a():
            pass

        def d0b():
            pass

        def d1a(d0a: str = Depends(d0a)):
            pass

        def d1b(d0b: str = Depends(d0b)):
            pass

        def d2(d1a: str = Depends(d1a), d1b: str = Depends(d1b)):
            pass

        diagraph = Diagraph(d2)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0a, d0b, d1a, d1b, d2]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (
                    d0a,
                    d0b,
                ),
            ),
            (
                1,
                (
                    d1a,
                    d1b,
                ),
            ),
            (2, (d2,)),
            (
                -3,
                (
                    d0a,
                    d0b,
                ),
            ),
            (
                -2,
                (
                    d1a,
                    d1b,
                ),
            ),
            (-1, (d2,)),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer
