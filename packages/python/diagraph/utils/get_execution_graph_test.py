import pytest

from ..classes.diagraph import Diagraph
from ..classes.graph import Graph
from ..classes.types import KeyIdentifier
from .depends import Depends
from .get_execution_graph import get_execution_graph

complicated_graph_def = {
    "d0b": [],
    "d1c": ["d0b"],
    "d2d": ["d1c"],
    "d3a": ["d2d"],
    "d0a": [],
    "d1a": ["d0a"],
    "d1b": ["d0b"],
    "d2a": ["d1a"],
    "d2b": ["d1a", "d1c"],
    "d2c": ["d1c"],
}


def describe_execution_graph():
    @pytest.mark.parametrize(
        ("graph_def", "starting_nodes", "expectation"),
        [
            # single node
            ({"a": []}, ["a"], [["a"]]),
            # two independent nodes
            ({"a": [], "b": []}, ["a"], [["a"]]),
            ({"a": [], "b": []}, ["b"], [["b"]]),
            ({"a": [], "b": []}, ["a", "b"], [["a", "b"]]),
            ({"a": [], "b": []}, ["b", "a"], [["b", "a"]]),
            # two dependent nodes
            ({"b": ["a"]}, ["a"], [["a"], ["b"]]),
            (
                {"b": ["a"]},
                ["b"],
                [
                    ["b"],
                ],
            ),
            ({"b": ["a"]}, ["a", "b"], [["a"], ["b"]]),
            ({"b": ["a"]}, ["b", "a"], [["a"], ["b"]]),
            # three dependent nodes
            ({"c": ["b"], "b": ["a"]}, ["a"], [["a"], ["b"], ["c"]]),
            ({"c": ["b"], "b": ["a"]}, ["b"], [["b"], ["c"]]),
            ({"c": ["b"], "b": ["a"]}, ["c"], [["c"]]),
            ({"c": ["b"], "b": ["a"]}, ["a", "b"], [["a"], ["b"], ["c"]]),
            ({"c": ["b"], "b": ["a"]}, ["a", "c"], [["a"], ["b"], ["c"]]),
            ({"c": ["b"], "b": ["a"]}, ["b", "c"], [["b"], ["c"]]),
            # one independent and two dependent nodes
            ({"b": ["a"], "c": ["a"]}, ["a"], [["a"], ["b", "c"]]),
            ({"b": ["a"], "c": ["a"]}, ["b"], [["b"]]),
            ({"b": ["a"], "c": ["a"]}, ["c"], [["c"]]),
            ({"b": ["a"], "c": ["a"]}, ["a", "b"], [["a"], ["b", "c"]]),
            ({"b": ["a"], "c": ["a"]}, ["a", "c"], [["a"], ["b", "c"]]),
            ({"b": ["a"], "c": ["a"]}, ["b", "c"], [["b", "c"]]),
            # one dependent and two independent nodes
            ({"c": ["a", "b"]}, ["a"], [["a"], ["c"]]),
            ({"c": ["a", "b"]}, ["b"], [["b"], ["c"]]),
            ({"c": ["a", "b"]}, ["c"], [["c"]]),
            ({"c": ["a", "b"]}, ["a", "b"], [["a", "b"], ["c"]]),
            ({"c": ["a", "b"]}, ["c", "a"], [["a"], ["c"]]),
            ({"c": ["a", "b"]}, ["a", "c"], [["a"], ["c"]]),
            ({"c": ["a", "b"]}, ["c", "b"], [["b"], ["c"]]),
            ({"c": ["a", "b"]}, ["b", "c"], [["b"], ["c"]]),
            # three connected nodes
            ({"b": ["a"], "c": ["a", "b"]}, ["a"], [["a"], ["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["b"], [["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["c"], [["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["a", "b"], [["a"], ["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["b", "a"], [["a"], ["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["a", "c"], [["a"], ["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["c", "a"], [["a"], ["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["b", "c"], [["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["c", "b"], [["b"], ["c"]]),
            ({"b": ["a"], "c": ["a", "b"]}, ["a", "b", "c"], [["a"], ["b"], ["c"]]),
            # two branches that converge
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["a"],
                [["a"], ["b"], ["c"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["b"],
                [["b"], ["c"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["c"],
                [["c"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["d"],
                [["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["e"],
                [["e"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["a", "e"],
                [["a", "e"], ["b"], ["c"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["b", "e"],
                [["b", "e"], ["c"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["c", "e"],
                [["c", "e"], ["d"]],
            ),
            (
                {"d": ["c", "e"], "c": ["b"], "b": ["a"]},
                ["a", "b", "c", "d", "e"],
                [["a", "e"], ["b"], ["c"], ["d"]],
            ),
            # complicated raph
            (
                complicated_graph_def,
                ["d3a"],
                [["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d2d"],
                [["d2d"], ["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d3a", "d2d"],
                [["d2d"], ["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d2d", "d3a"],
                [["d2d"], ["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d2c"],
                [["d2c"]],
            ),
            (
                complicated_graph_def,
                ["d2b"],
                [["d2b"]],
            ),
            (
                complicated_graph_def,
                ["d2a"],
                [["d2a"]],
            ),
            (
                complicated_graph_def,
                ["d1a"],
                [
                    ["d1a"],
                    ["d2a", "d2b"],
                ],
            ),
            (
                complicated_graph_def,
                ["d1a", "d1b"],
                [
                    ["d1a", "d1b"],
                    ["d2a", "d2b"],
                ],
            ),
            (
                complicated_graph_def,
                ["d1a", "d1c"],
                [["d1a", "d1c"], ["d2a", "d2b", "d2d", "d2c"], ["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d1a", "d1c", "d3a"],
                [["d1a", "d1c"], ["d2a", "d2b", "d2d", "d2c"], ["d3a"]],
            ),
            (
                complicated_graph_def,
                ["d1a", "d3a"],
                [["d1a", "d3a"], ["d2a", "d2b"]],
            ),
            (
                complicated_graph_def,
                ["d0a"],
                [["d0a"], ["d1a"], ["d2a", "d2b"]],
            ),
            (
                complicated_graph_def,
                ["d0b"],
                [["d0b"], ["d1c", "d1b"], ["d2d", "d2b", "d2c"], ["d3a"]],
            ),
        ],
    )
    def test_it_gets_execution_graph_for_nodes(graph_def, starting_nodes, expectation):
        def get_key_for_fn(fn: KeyIdentifier):
            return fn

        execution_graph = list(
            get_execution_graph(Graph(graph_def), starting_nodes, get_key_for_fn),
        )

        try:
            assert execution_graph == expectation
        except Exception as e:
            print(f"graph_def: {graph_def}")
            print(f"starting_nodes: {starting_nodes}")
            print(f"expectation: {expectation}")
            print(f"execution_graph: {execution_graph}")
            raise e

    def test_it_gets_execution_graph_for_diagraph_node_group():
        def a():
            return "a"

        def b(a=Depends(a)):
            return "b"

        def c(a=Depends(a)):
            return "c"

        dg = Diagraph(b, c)
        group = dg[0]

        execution_graph = list(
            get_execution_graph(dg.__graph__, group, dg.get_fn_for_key),
        )

        assert execution_graph == [[a], [b, c]]
