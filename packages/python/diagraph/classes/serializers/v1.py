import inspect
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel
from pydantic.functional_validators import field_validator

from ...utils.depends import FnDependency
from ..types import Fn
from .get_fn import dump_fn, get_fn

Vars = dict[str, Any]

# if TYPE_CHECKING:
#     from ..diagraph import Diagraph


class V1NodeConfig(BaseModel):
    fn: str
    inputs: list[str] | None = None
    args: None | Vars = None
    is_terminal: bool = False


class V1Config(BaseModel):
    nodes: dict[str, V1NodeConfig]
    args: None | Vars = None
    # MyNumber = Annotated[int, AfterValidator(double), AfterValidator(check_squares)]

    @field_validator("nodes", mode="before")
    def nodes_check(cls, _nodes):
        terminal_nodes = []
        if isinstance(_nodes, dict) is False:
            raise ValueError('validation error: "nodes" must be a dict')
        nodes = {}
        for key, node in _nodes.items():
            if isinstance(node, dict) is False:
                raise ValueError(f'validation error: "node" for {key} must be a dict')
            nodes[key] = V1NodeConfig(**node)
            if nodes[key].is_terminal:
                terminal_nodes.append(key)

        if len(terminal_nodes) == 0:
            raise ValueError(
                'validation error: at least one node must be marked as terminal by setting "is_terminal" to True',
            )
        return nodes


def collect_dependencies(fn: Callable) -> list[FnDependency]:
    dependencies: list[FnDependency] = []
    for parameter in inspect.signature(fn).parameters.values():
        if parameter.default is not None and parameter.default is not inspect._empty:
            if isinstance(parameter.default, FnDependency):
                dependencies.append(parameter.default.dependency)
    return dependencies


def collect_string_dependencies(fn: Callable) -> list[str]:
    dependencies = collect_dependencies(fn)
    return [d if isinstance(d, str) else d.__name__ for d in dependencies]


def serialize(diagraph: Any) -> dict[str, Any]:
    nodes = {}
    for node in diagraph.nodes:
        inputs = collect_string_dependencies(node.fn)
        nodes[node.fn.__name__] = {
            "fn": dump_fn(node.fn),
            # TODO: need to supply inputs, _and then_ does deserialize know how to read a Depends?
            "inputs": inputs if len(inputs) > 0 else None,
            "is_terminal": node.key in [n.key for n in diagraph.terminal_nodes],
        }
    config = V1Config(
        nodes=nodes,
        args=None,
    ).model_dump(exclude_none=True, exclude_defaults=True)
    return {
        **config,
        "version": "1",
    }


def build_vars(local_vars: Vars | None, args: Vars | None) -> Vars:
    built_vars = {}
    for v in [local_vars, args]:
        if v is not None:
            built_vars = {**built_vars, **v}
    return built_vars


def deserialize(config: dict) -> tuple[list[Fn], dict[str, Fn], None | Vars]:
    Config = V1Config(**config)
    terminal_nodes: list[Fn] = []
    node_mapping: dict[str, Fn] = {}

    for key, node in Config.nodes.items():
        fn = get_fn(
            node.fn,
            fn_name=None,
            node_args=node.args,
        )
        if node.is_terminal:
            terminal_nodes.append(fn)
        node_mapping[key] = fn

    kwargs = {}
    if Config.args:
        kwargs = {
            "llm": Config.args.get("llm", None),
            "error": Config.args.get("error", None),
            "log": Config.args.get("log", None),
        }

    return terminal_nodes, node_mapping, kwargs
