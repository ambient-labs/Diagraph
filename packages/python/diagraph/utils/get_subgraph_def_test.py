import pytest

from ..classes.graph import Graph
from .get_subgraph_def import get_subgraph_def


def describe_get_subgraph_def():
    @pytest.mark.parametrize(
        ("graph_def", "starting_nodes", "expectation"),
        [
            # slice
            ({"b": ["a"]}, ["a"], {"b": ["a"], "a": []}),
            ({"b": ["a"]}, ["a", "b"], {"b": ["a"], "a": []}),
            ({"b": ["a"]}, ["b"], {"b": []}),
            # three dependent nodes
            ({"b": ["a"], "c": ["b"]}, ["a"], {"a": [], "b": ["a"], "c": ["b"]}),
            ({"b": ["a"], "c": ["b"]}, ["b"], {"b": [], "c": ["b"]}),
            ({"b": ["a"], "c": ["b"]}, ["c"], {"c": []}),
            ({"b": ["a"], "c": ["b"]}, ["a", "b"], {"a": [], "b": ["a"], "c": ["b"]}),
            ({"b": ["a"], "c": ["b"]}, ["a", "c"], {"a": [], "b": ["a"], "c": ["b"]}),
            ({"b": ["a"], "c": ["b"]}, ["b", "c"], {"b": [], "c": ["b"]}),
            # one independent and two dependent nodes
            ({"b": ["a"], "c": ["a"]}, ["a"], {"a": [], "b": ["a"], "c": ["a"]}),
            ({"b": ["a"], "c": ["a"]}, ["b"], {"b": []}),
            ({"b": ["a"], "c": ["a"]}, ["c"], {"c": []}),
            ({"b": ["a"], "c": ["a"]}, ["b", "c"], {"c": [], "b": []}),
            ({"b": ["a"], "c": ["a"]}, ["a", "b"], {"b": ["a"], "a": [], "c": ["a"]}),
            ({"b": ["a"], "c": ["a"]}, ["a", "c"], {"c": ["a"], "a": [], "b": ["a"]}),
            # one dependent and two independent nodes
            ({"c": ["a", "b"]}, ["a"], {"c": ["a"], "a": []}),
            ({"c": ["a", "b"]}, ["b"], {"c": ["b"], "b": []}),
            ({"c": ["a", "b"]}, ["c"], {"c": []}),
            ({"c": ["a", "b"]}, ["a", "b"], {"c": ["a", "b"], "a": [], "b": []}),
            ({"c": ["a", "b"]}, ["a", "c"], {"c": ["a"], "a": []}),
            ({"c": ["a", "b"]}, ["b", "c"], {"c": ["b"], "b": []}),
            # three connected nodes
            (
                {"b": ["a"], "c": ["a", "b"]},
                ["a"],
                {"b": ["a"], "c": ["a", "b"], "a": []},
            ),
            ({"b": ["a"], "c": ["a", "b"]}, ["b"], {"b": [], "c": ["b"]}),
            ({"b": ["a"], "c": ["a", "b"]}, ["c"], {"c": []}),
            (
                {"b": ["a"], "c": ["a", "b"]},
                ["a", "b"],
                {
                    "a": [],
                    "b": ["a"],
                    "c": ["a", "b"],
                },
            ),
            (
                {"b": ["a"], "c": ["a", "b"]},
                ["a", "c"],
                {
                    "a": [],
                    "b": ["a"],
                    "c": ["a", "b"],
                },
            ),
            ({"b": ["a"], "c": ["a", "b"]}, ["b", "c"], {"b": [], "c": ["b"]}),
        ],
    )
    def test_it_gets_a_subgraph(graph_def, starting_nodes, expectation):
        subgraph = get_subgraph_def(Graph(graph_def), starting_nodes)
        subgraph = {key: list(val) for key, val in subgraph.items()}

        try:
            assert subgraph == expectation
        except Exception as e:
            print(f"graph_def: {graph_def}")
            print(f"starting_nodes: {starting_nodes}")
            print(f"expectation: {expectation}")
            print(f"subgraph: {subgraph}")
            raise e
