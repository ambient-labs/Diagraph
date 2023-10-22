from __future__ import annotations

from collections.abc import Mapping
from typing import Generic, TypeVar

import networkx as nx

from .ordered_set import OrderedSet

K = TypeVar("K")


class Graph(Generic[K]):
    __G__: nx.DiGraph
    __key_to_int__: dict[K, int]
    graph_def: dict[K, list[K]]

    def __init__(self, graph_def: Mapping[K, list[K] | OrderedSet[K]]):
        self.graph_def = {key: list(val) for key, val in graph_def.items()}
        self.__key_to_int__ = {}
        self.__G__ = nx.convert_node_labels_to_integers(
            nx.DiGraph(self.graph_def),
            label_attribute="ref",
        )

        for int_representation in self.__G__.nodes():
            ref = self.__G__.nodes[int_representation]["ref"]
            self.__key_to_int__[ref] = int_representation

    def get_nodes(self) -> list[K]:
        return [self.__G__.nodes[int_rep]["ref"] for int_rep in self.__G__.nodes()]

    def get_int_key_for_node(self, key: K) -> int:
        return self.__key_to_int__[key]

    def get_node_for_int_key(self, key: int) -> K:
        return self.__G__.nodes[key]["ref"]

    def __getitem__(self, key: K):
        return key

    def __setitem__(self, old: K, new: K):
        self.__key_to_int__[new] = self.__key_to_int__[old]
        del self.__key_to_int__[old]
        self.__G__.nodes[self.__key_to_int__[new]]["ref"] = new

    def to_json(self):
        return nx.node_link_data(self.__G__)

    def in_edges(self, key: K):
        int_key = self.get_int_key_for_node(key)
        int_representations = [i for i, _ in list(self.__G__.in_edges(int_key))]
        return [self.get_node_for_int_key(i) for i in int_representations]

    def out_edges(self, int_key: K):
        node = self.get_int_key_for_node(int_key)
        int_representations = [i for _, i in list(self.__G__.out_edges(node))]
        return [self.get_node_for_int_key(i) for i in int_representations]

    @property
    def nodes(self) -> list[K]:
        return [self.get_node_for_int_key(i) for i in self.__G__.nodes()]

    @property
    def root_nodes(self) -> list[K]:
        int_keys: list[int] = [
            n for n in self.__G__.nodes() if self.__G__.out_degree(n) == 0
        ]
        return [self.get_node_for_int_key(i) for i in int_keys]

    def _repr_html_(self) -> str:
        return nx.draw(
            self.__G__,
        )

    def __str__(self) -> str:
        name_mapping = {
            key: self.get_node_for_int_key(key).__name__ for key in self.__G__.nodes()
        }
        return "\n".join(
            list(
                nx.generate_network_text(
                    nx.relabel_nodes(self.__G__, name_mapping).reverse(),
                    vertical_chains=True,
                    ascii_only=True,
                    with_labels=True,
                ),
            ),
        )
