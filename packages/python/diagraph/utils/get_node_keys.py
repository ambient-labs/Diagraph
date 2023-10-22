from __future__ import annotations

from ..classes.diagraph_node_group import DiagraphNodeGroup
from ..classes.types import Fn


def get_node_keys(node_keys: list[Fn] | DiagraphNodeGroup) -> list[Fn]:
    """
    Extracts node keys from either a list of functions or a DiagraphNodeGroup.

    Parameters:
    - node_keys (list[Fn] | DiagraphNodeGroup): Either a list of functions or a DiagraphNodeGroup.

    Returns:
    list[Fn]: The list of function keys.
    """
    if isinstance(node_keys, DiagraphNodeGroup):
        return [n.key for n in node_keys.nodes]
    return node_keys
