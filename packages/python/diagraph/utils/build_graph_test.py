from typing import Any

from .build_graph import build_graph, get_dependencies
from .depends import Depends


class MockDiagraph:
    use_string_keys = False

    def __init__(self, use_string_keys: bool = False):
        self.use_string_keys = use_string_keys


dg: Any = MockDiagraph()


def test_returns_an_empty_graph():
    assert build_graph(dg, terminal_nodes=()) == {}


def test_returns_a_single_node_graph_and_ignores_return_key():
    def foo() -> str:
        return "foo"

    assert build_graph(dg, terminal_nodes=(foo,)) == {foo: set()}


def test_works_with_a_stub(mocker):
    mock_instance = mocker.Mock()

    def stub():
        return mock_instance()

    assert build_graph(dg, terminal_nodes=(stub,)) == {stub: set()}


def test_returns_a_linear_graph():
    def foo():
        return "foo"

    def bar(foo_arg: str = Depends(foo)) -> str:
        return f"bar: {foo_arg}"

    assert build_graph(dg, terminal_nodes=(bar,)) == {foo: set(), bar: {foo}}


def test_returns_a_linear_graph_with_default_syntax_and_ignores_default_non_depends():
    def foo():
        return "foo"

    def bar(foo_arg: str = Depends(foo), bar_arg: str = "bar") -> str:
        return f"bar: {foo_arg}: {bar_arg}"

    assert build_graph(dg, terminal_nodes=(bar,)) == {foo: set(), bar: {foo}}


def test_returns_a_multistep_linear_graph():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(bar: str = Depends(bar)) -> str:
        return f"baz: {bar}"

    assert build_graph(dg, terminal_nodes=(baz,)) == {
        foo: set(),
        bar: {foo},
        baz: {bar},
    }


def test_returns_an_interconnected_graph():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(foo: str = Depends(foo), bar: str = Depends(bar)) -> str:
        return f"baz: {foo} {bar}"

    assert build_graph(dg, terminal_nodes=(baz,)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
    }


def test_returns_a_very_interconnected_graph():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(foo: str = Depends(foo), bar: str = Depends(bar)) -> str:
        return f"baz: {foo} {bar}"

    def qux(foo: str = Depends(foo), baz: str = Depends(baz)) -> str:
        return f"qux: {foo} {baz}"

    assert build_graph(dg, terminal_nodes=(qux,)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
        qux: {foo, baz},
    }


def test_handles_multiple_node_args():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(foo: str = Depends(foo), bar: str = Depends(bar)) -> str:
        return f"baz: {foo} {bar}"

    def qux(foo: str = Depends(foo), bar: str = Depends(bar)) -> str:
        return f"qux: {foo} {bar}"

    assert build_graph(dg, terminal_nodes=(baz, qux)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
        qux: {foo, bar},
    }


def test_ignores_message_order():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(bar: str = Depends(bar), foo: str = Depends(foo)) -> str:
        return f"baz: {foo} {bar}"

    assert build_graph(dg, terminal_nodes=(baz,)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
    }


def test_it_handles_strings_at_beginning():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(
        string_arg: str,
        bar: str = Depends(bar),
        foo: str = Depends(foo),
    ) -> str:
        return f"baz: {string_arg} {foo} {bar}"

    assert build_graph(dg, terminal_nodes=(baz,)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
    }


def test_it_handles_strings_at_end():
    def foo():
        return "foo"

    def bar(foo: str = Depends(foo)) -> str:
        return f"bar: {foo}"

    def baz(
        string_arg: str,
        bar=Depends(bar),
        foo=Depends(foo),
    ) -> str:
        return f"baz: {string_arg} {foo} {bar}"

    assert build_graph(dg, terminal_nodes=(baz,)) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
    }


def describe_get_dependencies():
    def test_it_gets_dependencies():
        def foo():
            return "foo"

        def bar():
            return "bar"

        def fn(a: int = Depends(foo), b: str = Depends(bar)):
            return a

        dg = MockDiagraph(use_string_keys=False)

        dependencies = [
            d
            for d in list(
                get_dependencies(
                    dg,
                    fn,
                ),
            )
        ]
        assert dependencies == [
            foo,
            bar,
        ]

    def test_it_gets_dependencies_when_using_string_key():
        def foo():
            return "foo"

        def bar():
            return "bar"

        def fn(a: int = Depends("foo"), b: str = Depends("bar")):
            return a

        dg = MockDiagraph(use_string_keys=True)

        dependencies = [
            d
            for d in list(
                get_dependencies(
                    dg,
                    node=fn,
                    node_dict={
                        "foo": foo,
                        "bar": bar,
                        "fn": fn,
                    },
                ),
            )
        ]
        assert dependencies == [
            foo,
            bar,
        ]
