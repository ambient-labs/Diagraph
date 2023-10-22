from __future__ import annotations

from ..classes.diagraph_node import DiagraphNode
from ..classes.diagraph_node_group import DiagraphNodeGroup


def validate_node_ancestor(node: DiagraphNode) -> None:
    """
    Validates that a given node's result is not None.

    Parameters:
    - node (DiagraphNode): The node to be validated.

    Raises:
    - Exception: If the node's result is None, indicating a missing result.
    """
    try:
        assert node.result
    except Exception:
        raise Exception(
            "An ancestor is missing a result, run the traversal first",
        ) from None


def validate_node_ancestors(node_group: DiagraphNodeGroup) -> None:
    """
    Validates the results of ancestors for each node in a group.

    Parameters:
    - node_group (DiagraphNodeGroup): The group of nodes to be validated.

    Raises:
    - Exception: If any ancestor of a node in the group has a missing result.
    """
    for node in node_group.nodes:
        for ancestor in node.ancestors:
            validate_node_ancestor(ancestor)
