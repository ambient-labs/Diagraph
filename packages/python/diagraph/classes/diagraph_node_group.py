from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .diagraph_node import DiagraphNode
from .types import Fn, KeyIdentifier, Result

if TYPE_CHECKING:
    from .diagraph import Diagraph


class DiagraphNodeGroup:
    """A layer of DiagraphNodes representing a set of related nodes in a Diagraph."""

    diagraph: Diagraph
    nodes: tuple[DiagraphNode, ...]

    def __init__(
        self, diagraph: Diagraph, *node_keys: KeyIdentifier | DiagraphNode,
    ) -> None:
        """
        Initialize a DiagraphNodeGroup.

        Args:
            diagraph (Any): The Diagraph instance that contains this layer.
            *node_keys (Key): Variable number of keys representing nodes in the layer.
        """
        self.diagraph = diagraph
        nodes = []
        for node in node_keys:
            if isinstance(node, DiagraphNode):
                nodes.append(node)
            else:
                nodes.append(DiagraphNode(self.diagraph, node))
        self.nodes = tuple(nodes)

    def __iter__(self) -> Iterator[DiagraphNode]:
        """
        Create an iterator for the nodes in the layer.

        Returns:
            iter: An iterator for the nodes in the layer.
        """
        return iter(self.nodes)

    def __str__(self) -> str:
        """
        Get a string representation of the DiagraphNodeGroup.

        Returns:
            str: A string representation of the layer.
        """
        return f"({[str(n) for n in self.nodes]})"

    def __getitem__(self, key: Fn | int) -> DiagraphNode:
        """
        Get a specific node or a subset of nodes from the layer.

        Args:
            key (Key | int): The key, index, or slice to access the nodes.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The requested node or nodes.
        """
        if isinstance(key, int):
            return self.nodes[key]

        for node in self.nodes:
            if node.key == key:
                return node
        raise Exception(f"No node for key {key}")

    def __len__(self) -> int:
        """
        Get the number of nodes in the layer.

        Returns:
            int: The number of nodes in the layer.
        """
        return len(self.nodes)

    def __contains__(self, item: Fn) -> bool:
        """
        Check if a specific node key is present in the layer.

        Args:
            item (Key): The node key to check.

        Returns:
            bool: True if the key is in the layer, False otherwise.
        """
        for node in self.nodes:
            if node.key == item:
                return True
        return False

    def run(self, *input_args, **kwargs) -> Diagraph:
        """
        Run the Diagraph starting from the nodes in this layer.

        Args:
            *input_args: Input arguments to be passed to the Diagraph.

        Returns:
            None
        """

        self.diagraph.__run_from__(self, *input_args, **kwargs)
        return self.diagraph

    @property
    def result(self) -> Result | tuple[Result, ...]:
        """
        Get the results of the nodes in the layer.

        Returns:
            Any or tuple[Any]: The result of the nodes, either as a single value or a tuple of values.
        """
        results = [node.result for node in self.nodes]
        if len(results) == 1:
            return results[0]
        return tuple(results)

    @property
    def prompt(self) -> str | tuple[str, ...]:
        """
        Get the prompts associated with the nodes in the layer.

        Returns:
            str or tuple[str]: The prompt of the nodes, either as a single string or a tuple of strings.
        """
        prompts = [node.prompt for node in self.nodes]
        if len(prompts) == 1:
            return prompts[0]
        return tuple(prompts)

    @property
    def tokens(self) -> int | tuple[int, ...]:
        """
        Get the number of tokens in the prompts associated with the nodes in the layer.

        Returns:
            int or tuple[int]: The number of tokens for each node's prompt.
        """
        tokens = [node.tokens for node in self.nodes]
        if len(tokens) == 1:
            return tokens[0]
        return tuple(tokens)

    @result.setter
    def result(self, values: tuple[Result, ...] | list[Result]) -> None:
        """
        Set the results for the nodes in the layer.

        Args:
            values (Any or tuple[Any]): The values to set as results for the nodes.

        Raises:
            Exception: If the number of values does not match the number of nodes.
        """
        if isinstance(values, str):
            if len(self.nodes) != 1:
                raise Exception(
                    " ".join(
                        [
                            f"You provided a string as a value but the layer has {len(self.nodes)} nodes.",
                            "Setting a string value is only supported for a single node."
                            f"Instead, provide a tuple of values matching of length {len(self.nodes)}",
                        ],
                    ),
                )
            self.nodes[0].result = values
        else:
            if len(self.nodes) != len(values):
                raise Exception(
                    f"Number of results ({len(values)}) does not match number of nodes ({len(self.nodes)})",
                )

            for node, value in zip(self.nodes, values, strict=True):
                node.result = value
