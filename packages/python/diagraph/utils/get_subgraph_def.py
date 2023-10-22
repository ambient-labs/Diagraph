from __future__ import annotations

from typing import TypeVar

from ..classes.graph import Graph
from ..classes.ordered_set import OrderedSet

K = TypeVar("K")


def get_subgraph_def(
    graph: Graph[K],
    node_keys: list[K],
    seen: set | None = None,
    subgraph: dict[K, OrderedSet[K]] | None = None,
) -> dict[K, OrderedSet[K]]:
    """
    Recursively generates a subgraph definition for a given set of nodes and their ancestors.

    Parameters:
    - graph (Graph): The directed graph from which to extract the subgraph.
    - node_keys (List[K]): A list of node keys for which to generate the subgraph.
    - seen (Optional[Set[K]]): A set to keep track of nodes that have already been processed.
      Default is None, and an empty set is created.
    - subgraph (Optional[Dict[K, OrderedSet[K]]]): The subgraph definition being constructed.
      Default is None, and an empty dictionary is created.

    Returns:
    Dict[K, OrderedSet[K]]: The subgraph definition, where keys are nodes and values are their ancestors.
    """
    if subgraph is None:
        subgraph = {}

    if seen is None:
        seen = set()

    for key in node_keys:
        if key not in seen:
            if subgraph.get(key) is None:
                subgraph[key] = OrderedSet()

            children = graph.in_edges(key)
            for child in children:
                if subgraph.get(child) is None:
                    subgraph[child] = OrderedSet()
                subgraph[child].add(key)
            subgraph = get_subgraph_def(graph, children, seen, subgraph)
            seen.add(key)

    return subgraph
