from __future__ import annotations

import json
import pickle
from collections.abc import Callable
from pathlib import Path
from typing import overload

from ..decorators.prompt import set_default_llm
from ..llm.llm import LLM
from ..utils.build_graph import NodeDict, build_graph_mapping
from ..utils.get_execution_graph import get_execution_graph
from ..utils.get_filetype import get_filetype
from ..utils.validate_node_ancestors import validate_node_ancestors
from ..visualization.render_repr_html import render_repr_html
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .diagraph_state.diagraph_state import DiagraphState
from .diagraph_state.diagraph_state_record import (
    DiagraphStateValueEmpty,
)
from .diagraph_state.types import StateValue
from .graph import Graph
from .graph_executor import GraphExecutor
from .serializers import DEFAULT_SERIALIZER, SERIALIZERS
from .types import ErrorHandler, Fn, KeyIdentifier, LogHandler, Result

global_log_fn: LogHandler | None = None


def set_global_log(log_fn: None | LogHandler) -> None:
    global global_log_fn
    global_log_fn = log_fn


global_error_fn: ErrorHandler | None = None


def set_global_error(error_fn: None | ErrorHandler) -> None:
    global global_error_fn
    global_error_fn = error_fn


MAX_WORKERS = 5


class Diagraph:
    """A directed acyclic graph (Diagraph) for managing
    and executing a graph of functions."""

    __graph__: Graph[Fn]
    __state__: DiagraphState

    terminal_nodes: tuple[DiagraphNode, ...]
    log_handler: LogHandler | None
    error_handler: ErrorHandler | None
    fns: dict[KeyIdentifier, Fn]
    llm: LLM | None
    max_workers: int = MAX_WORKERS
    use_string_keys: bool
    created_from_json: bool

    def __init__(
        self,
        *terminal_fns: Fn,
        log=None,
        error=None,
        llm=None,
        node_dict: None | NodeDict = None,
        use_string_keys=False,
        created_from_json=False,
        max_workers=MAX_WORKERS,
    ) -> None:
        """
        Initialize a Diagraph.

        Args:
            terminal_nodes: The terminal nodes of the graph.
            log (LogHandler | None): A logging function for capturing log messages.
            error (ErrorHandler | None): An error handling function.
            use_string_keys (bool): Whether to use string keys
                                    for functions in the graph.
        """
        self.__state__ = DiagraphState()
        self.max_workers = max_workers
        self.use_string_keys = use_string_keys
        self.created_from_json = created_from_json
        if use_string_keys and node_dict is None:
            raise Exception(
                "If relying on string keys, a dict mapping of all functions must be provided",
            )
        self.fns = {}
        self.llm = llm

        graph_def, self.fns = build_graph_mapping(
            self,
            terminal_fns,
            # optionally, provide a dict of _all_ nodes, which
            # is required if relying on string keys to build the graph
            node_dict=node_dict,
        )
        self.__graph__ = Graph(graph_def)

        self.terminal_nodes = tuple(DiagraphNode(self, fn) for fn in terminal_fns)
        self.log_handler = log or global_log_fn
        self.error_handler = error

    def get_fn_for_key(self, key: KeyIdentifier) -> Fn:
        if self.use_string_keys:
            fn = self.fns.get(key)
            if fn is None:
                raise Exception(f"No fn found for key {key}. Fns: {self.fns}")
            return fn

        if isinstance(key, Callable):
            return key
        raise Exception(f"Invalid key: {key}")

    def get_key_for_fn(self, fn: KeyIdentifier) -> KeyIdentifier:
        if self.use_string_keys:
            if isinstance(fn, str):
                return fn
            return fn.__name__
        if isinstance(fn, str):
            raise Exception(
                f"Cannot use string key for function {fn}. "
                "Set use_string_keys=True to use string keys.",
            )
        return fn

    def _repr_html_(self) -> str:
        return render_repr_html(self)

    def get_children_of_node(self, node: DiagraphNode | Fn) -> list[DiagraphNode]:
        key = node.key if isinstance(node, DiagraphNode) else node
        return [
            DiagraphNode(self, node)
            for node in self.__graph__.in_edges(self.get_fn_for_key(key))
        ]

    def get_ancestors_of_node(self, node: DiagraphNode | Fn) -> list[DiagraphNode]:
        key = node.key if isinstance(node, DiagraphNode) else node
        return [
            DiagraphNode(self, node)
            for node in self.__graph__.out_edges(self.get_fn_for_key(key))
        ]

    @overload
    def __getitem__(self, key: int) -> DiagraphNodeGroup:
        ...

    @overload
    def __getitem__(self, key: tuple[KeyIdentifier, ...]) -> DiagraphNodeGroup:
        ...

    @overload
    def __getitem__(self, key: KeyIdentifier) -> DiagraphNode:
        ...

    def __getitem__(
        self,
        key: KeyIdentifier | int | tuple[KeyIdentifier, ...],
    ) -> DiagraphNode | DiagraphNodeGroup:
        """
        Retrieve a DiagraphNode or DiagraphNodeGroup associated with a function or depth key.

        Args:
            key (str | Fn | int | tuple): A function, string for a function, or depth key.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The DiagraphNode or
            DiagraphNodeGroup associated with the key.
        """
        if isinstance(key, int):
            execution_graph = list(
                get_execution_graph(
                    self.__graph__,
                    self.__graph__.root_nodes,
                    self.get_fn_for_key,
                ),
            )

            if key < 0:
                key = len(execution_graph) + key

            node_keys = execution_graph[key]
            return DiagraphNodeGroup(self, *node_keys)

        if isinstance(key, tuple):
            return DiagraphNodeGroup(self, *key)

        if self.use_string_keys:
            if isinstance(key, str):
                return DiagraphNode(self, key)

            if self.created_from_json:
                raise Exception(
                    " ".join(
                        [
                            "This Diagraph was created from JSON, and therefore functions must be specified",
                            "with their string names, _not_ the functions themselves.",
                            f'Instead of specifying the function {key}, specify its name "{key.__name__}"',
                        ],
                    ),
                )
            raise Exception(f"Invalid key: {key}, expected a str")
        if isinstance(key, Callable):
            return DiagraphNode(self, key)

        raise Exception(f"Invalid key: {key}, expected a callable")

    def run(self, *input_args, **kwargs) -> Diagraph:
        """
        Run the Diagraph from the beginning.

        Args:
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """

        root_nodes: list[Fn] = self.__graph__.root_nodes
        group = DiagraphNodeGroup(self, *root_nodes)
        self.__run_from__(group, *input_args, **kwargs)
        return self

    def __run_from__(
        self,
        group: DiagraphNodeGroup | DiagraphNode,
        *input_args,
        **input_kwargs,
    ) -> Diagraph:
        """
        Run the Diagraph from a specific node.

        Args:
            node_key (Fn | int): The node key or depth to start execution from.
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """
        starting_node_group = get_diagraph_node_group(self, group)
        self.__state__.add_timestamp()
        run = {
            "node_group": starting_node_group,
            "input": input_args,
            "kwargs": input_kwargs,
        }
        self.__state__["run"] = run

        validate_node_ancestors(starting_node_group)

        GraphExecutor(
            self,
            DiagraphNodeGroup(
                self,
                *next(
                    get_execution_graph(
                        self.__graph__,
                        starting_node_group,
                        self.get_fn_for_key,
                    ),
                ),
            ),
            input_args=input_args,
            input_kwargs=input_kwargs,
            max_workers=self.max_workers,
            global_error_fn=global_error_fn,
        )
        run["complete"] = True
        errors_encountered = self.error
        if errors_encountered is not None:
            if isinstance(errors_encountered, Exception):
                raise Exception(
                    f"Errors encountered. {errors_encountered} Call .error to see errors",
                )
            errors_encountered = [e for e in errors_encountered if e is not None]
            if len(errors_encountered) > 0:
                raise Exception(
                    f"Errors encountered. {errors_encountered} Call .error to see errors",
                )

        return self

    @property
    def __latest_run__(self):
        try:
            return self.__state__["run"]
        except Exception:
            raise Exception("Diagraph has not been run yet") from None

    @property
    def result(self) -> Result | tuple[Result, ...] | None:
        """
        Get the results of the terminal nodes.

        Returns:
            Any or tuple[Any]: The result of the terminal nodes, either as a single value or a tuple of values.
        """
        latest_run = self.__latest_run__
        if latest_run.get("complete") is True:
            results = [node.result for node in self.terminal_nodes]
            if len(results) == 1:
                return results[0]
            return tuple(results)
        return None

    @property
    def error(self) -> Exception | tuple[Exception | None, ...] | None:
        """
        Get the errors of the terminal nodes.

        Returns:
            Exception or tuple[Exception]: The errors of the terminal nodes,
            either as a single value or a tuple of values.
        """
        try:
            assert self.__state__["run"]

            errors = []
            for node in self.nodes:
                try:
                    errors.append(node.error)
                except Exception:  # noqa: PERF203
                    errors.append(None)
            if len(errors) == 0:
                return None
            if len(errors) == 1:
                return errors[0]
            return tuple(errors)
        except Exception:
            raise Exception("Diagraph has not been run yet") from None

    @property
    def nodes(self):
        return [DiagraphNode(self, node) for node in self.__graph__.nodes]

    def __setitem__(self, node_key: KeyIdentifier, fn: Fn) -> None:
        """
        Add a function to the Diagraph.

        Args:
            node_key (Key): The key associated with the function.
            fn (Fn): The function to add to the Diagraph.
        """
        self.__inc_timestamp__(DiagraphNode(self, node_key))
        self.fns[node_key] = fn

    def __inc_timestamp__(self, node: DiagraphNode):
        self.__state__.add_timestamp()

        def recurse_through_children(node: DiagraphNode, nodes: set[DiagraphNode]):
            nodes.add(node)
            for child in node.children:
                recurse_through_children(child, nodes)
            return nodes

        children = recurse_through_children(node, set())

        def clear(node: DiagraphNode) -> None:
            if node.__is_decorated__:
                self.__state__[("prompt", node.key)] = DiagraphStateValueEmpty()
            self.__state__[("result", node.key)] = DiagraphStateValueEmpty()
            self.__state__[("error", node.key)] = DiagraphStateValueEmpty()

        for child in children:
            clear(child)

    def __set_state__(self, node: DiagraphNode, key: str, value: StateValue) -> None:
        self.__inc_timestamp__(node)
        self.__state__[(key, node.key)] = value

    def __str__(self) -> str:
        """
        Get a string representation of the diagraph.

        Returns:
            str: The string representation of the diagraph.
        """

        graph = str(self.__graph__)
        return "\n".join(
            [
                "Diagraph " + "-" * 40,
                graph,
                "-" * (len("Diagraph ") + 40),
            ],
        )

    def to_json(self, version=DEFAULT_SERIALIZER):
        available_serializers = list(SERIALIZERS.keys())
        if str(version) not in available_serializers:
            raise Exception(
                f"Unsupported version: {version}. Available versions: {available_serializers}",
            )
        return SERIALIZERS[version]["serialize"](
            self,
        )

    @staticmethod
    def from_json(config: dict):
        if isinstance(config, dict) is False:
            raise Exception("Please pass a valid Diagraph configuration")
        version = config.get("version")
        available_serializers = list(SERIALIZERS.keys())
        if str(version) not in available_serializers:
            raise Exception(
                f"Unsupported version: {version}. Available versions: {available_serializers}",
            )

        terminal_nodes, node_mapping, kwargs = SERIALIZERS[str(version)]["deserialize"](
            config,
        )
        return Diagraph(
            *terminal_nodes,
            use_string_keys=True,
            created_from_json=True,
            node_dict=node_mapping,
            **kwargs,
        )

    def save(self, filepath: str | Path, filetype: str | None = None):
        filetype = get_filetype(filepath, filetype)

        mode = "wb" if filetype == "pickle" else "w"

        with Path(filepath).open(mode) as file_handle:
            if filetype == "json":
                json.dump(self.to_json(), file_handle)
            else:
                file_handle.write(pickle.dumps(self.to_json()))

    @staticmethod
    def load(filepath: str | Path, filetype: str | None = None):
        filetype = get_filetype(filepath, filetype)

        mode = "rb" if filetype == "pickle" else "r"

        with Path(filepath).open(mode) as file_handle:
            if filetype == "json":
                config = json.load(file_handle)
            else:
                contents = file_handle.read()
                unpickled_content = pickle.loads(contents)
                config = json.loads(unpickled_content)

        return Diagraph.from_json(config)

    @staticmethod
    def set_llm(llm: None | LLM) -> None:
        set_default_llm(llm)

    @staticmethod
    def set_log(log_fn: None | LogHandler) -> None:
        set_global_log(log_fn)

    @staticmethod
    def set_error(error_fn: None | ErrorHandler) -> None:
        set_global_error(error_fn)


def get_diagraph_node_group(
    diagraph: Diagraph,
    group: DiagraphNodeGroup | DiagraphNode,
) -> DiagraphNodeGroup:
    if not isinstance(group, DiagraphNodeGroup):
        return DiagraphNodeGroup(diagraph, group)
    return group
