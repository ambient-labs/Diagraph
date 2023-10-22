from __future__ import annotations

from collections.abc import Callable, Generator, Mapping
from typing import TYPE_CHECKING, TypeVar

from ..classes.diagraph_node import DiagraphNode
from ..classes.diagraph_node_group import DiagraphNodeGroup

# from packages.python.diagraph.classes.diagraph_node import DiagraphNode
# from ..classes.diagraph import Diagraph
from ..classes.graph import Graph
from ..classes.ordered_set import OrderedSet
from ..classes.types import Fn, KeyIdentifier
from .get_node_keys import get_node_keys
from .get_subgraph_def import get_subgraph_def

if TYPE_CHECKING:
    pass

K = TypeVar("K")


def ancestor_is_upstream_dependency(
    graph: Graph,
    potential_upstream_dependency: K,
    parent: K,
) -> bool:
    """
    Checks if a potential upstream dependency is an ancestor of a given node.

    Parameters:
    - graph (Graph): The directed graph.
    - potential_upstream_dependency (K): The potential upstream dependency node.
    - parent (K): The target node.

    Returns:
    bool: True if the potential upstream dependency is an ancestor of the target node, False otherwise.
    """
    for ancestor in graph.out_edges(potential_upstream_dependency):
        if (
            ancestor == parent
            or ancestor_is_upstream_dependency(graph, ancestor, parent) is True
        ):
            return True
    return False


def has_unexecuted_upstream_dependencies(
    graph: Graph,
    child: K,
    parent: K,
    seen: set[K],
) -> bool:
    """
    Checks if a node has unexecuted upstream dependencies with respect to a parent node.

    Parameters:
    - graph (Graph): The directed graph.
    - child (K): The child node.
    - parent (K): The parent node.
    - seen (set[K]): A set of nodes that have been seen.

    Returns:
    bool: True if the child has unexecuted upstream dependencies, False otherwise.
    """
    for ancestor in graph.out_edges(child):
        if (
            # parent != ancestor
            ancestor_is_upstream_dependency(graph, ancestor, parent)
            and ancestor not in seen
        ):
            return True
    return False


def get_execution_graph(
    graph: Graph[Fn],
    _node_keys: list[KeyIdentifier] | list[Fn] | DiagraphNodeGroup,
    # get_fn_for_key: Callable[[KeyIdentifier], Fn],
    get_fn_for_key: Callable,
) -> Generator[list[Fn], None, None]:
    """
    Generates a topological execution graph for a set of nodes in a directed graph.

    Parameters:
    - graph (Graph[Fn]): The directed graph.
    - _node_keys (list[Fn] | DiagraphNodeGroup): Either a list of functions or a DiagraphNodeGroup.

    Yields:
    Generator[list[Fn], None, None]: A generator of lists representing the topological order of execution.
    """
    fns = []
    for key in _node_keys:
        if isinstance(key, DiagraphNode):
            fns.append(get_fn_for_key(key.key))
        else:
            fns.append(get_fn_for_key(key))
    node_keys = get_node_keys(fns)
    subgraph_def: Mapping[Fn, OrderedSet[Fn]] = get_subgraph_def(graph, node_keys)
    subgraph: Graph[Fn] = Graph(subgraph_def)
    nodes = subgraph.root_nodes
    yield nodes

    seen = set(nodes)

    while len(nodes):
        out_edges: OrderedSet[Fn] = OrderedSet()
        for key in nodes:
            for child in subgraph.in_edges(key):
                if child not in seen:
                    # have all this children's ancestors been seen?
                    # a node may have upstream dependencies that have yet to be ran.
                    # these are distinct from ancestors, who may never be ran (e.g.,
                    # we have asked to run from a specific node, or an ancestor represents
                    # a different unrelated branch)
                    valid = True
                    for ancestor in subgraph.out_edges(child):
                        if ancestor not in seen:
                            valid = False
                            break
                    if valid:
                        out_edges.add(child)

        if len(out_edges) == 0:
            break

        yield list(out_edges)
        for edge in out_edges:
            seen.add(edge)
        nodes = out_edges
