from __future__ import annotations

import inspect
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING

from ..classes.ordered_set import OrderedSet
from ..classes.types import Fn
from .depends import FnDependency

if TYPE_CHECKING:
    from ..classes.diagraph import Diagraph

NodeDict = dict[str, Fn]


def get_dependencies(
    diagraph: Diagraph, node: Fn, node_dict: None | NodeDict = None,
) -> Generator[Fn, None, None]:
    """
    Extracts dependencies from the default values of a function's parameters.

    Parameters:
    - node (Fn): The function from which to extract dependencies.

    Yields:
    Generator[Fn, None, None]: A generator of functions representing the dependencies.
    """
    for val in inspect.signature(node).parameters.values():
        if isinstance(val.default, FnDependency):
            dep = val.default.dependency

            if diagraph.use_string_keys:
                if node_dict is None:
                    raise Exception(
                        "Cannot use string keys without providing a dictionary mapping",
                    )
                if isinstance(dep, str):
                    fn = node_dict.get(dep)
                    if fn is None:
                        raise Exception(
                            f'Function "{dep}" not found in nodes dictionary mapping',
                        )
                    yield fn
                else:
                    raise Exception(f"Dependency {dep} is not a string")
            else:
                if isinstance(dep, Callable):
                    yield dep
                else:
                    raise Exception(f"Dependency {dep} is not a callable function")


def build_graph(
    diagraph: Diagraph,
    terminal_nodes: tuple[Fn, ...],
    node_dict: None | NodeDict = None,
) -> dict[Fn, OrderedSet[Fn]]:
    """
    Builds a dependency graph for a set of functions.

    Parameters:
    - terminal_nodes (Fn): Variable-length argument list of functions to include in the graph.

    Returns:
    dict[Fn, OrderedSet[Fn]]: A dictionary representing the dependency graph,
    where keys are functions and values are their dependencies.
    """
    graph: dict[Fn, OrderedSet[Fn]] = {}
    seen = set()
    nodes: list[Fn] = list(terminal_nodes)
    for node in nodes:
        if isinstance(node, Callable) is False:
            raise Exception(f"Node {node} is not a callable function")
        if node not in graph:
            graph[node] = OrderedSet()
        if node not in seen:
            seen.add(node)
            for dep in get_dependencies(diagraph, node, node_dict):
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph


GetFnKey = Callable[[Fn], str | Fn]


def build_graph_mapping(
    diagraph: Diagraph,
    terminal_nodes: tuple[Fn, ...],
    node_dict: NodeDict | None = None,
):
    get_fn_key = diagraph.get_key_for_fn
    graph_def: dict[Fn, OrderedSet[Fn]] = build_graph(
        diagraph, terminal_nodes, node_dict,
    )
    # graph_mapping: dict[Fn, str | Fn] = dict()
    graph_def_keys: list[Fn] = list(graph_def.keys())
    fns = {}

    for item in graph_def_keys:
        fns[get_fn_key(item)] = item
        val = graph_def[item]
        new_val: OrderedSet[Fn] = OrderedSet()
        while len(val):
            _item = val.pop()
            new_val.add(_item)

        del graph_def[item]
        graph_def[item] = new_val
    return graph_def, fns
