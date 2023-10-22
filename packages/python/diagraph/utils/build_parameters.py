from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from ..classes.diagraph_state.diagraph_state_record import DiagraphStateValueEmpty
from ..classes.types import Fn
from .depends import FnDependency

if TYPE_CHECKING:
    from ..classes.diagraph import Diagraph


def build_parameters(
    diagraph: Diagraph,
    fn: Fn,
    provided_args: tuple,
    provided_kwargs: dict[Any, Any],
) -> tuple[list[Any], dict[str, Any]]:
    """
    Builds a list of parameters for a function based on its signature and provided arguments.

    Parameters:
    - diagraph (Diagraph): The directed graph representing the dependency structure.
    - fn (Fn): The function for which to build parameters.
    - input_args (Tuple): The input arguments provided when the function is called.

    Returns:
    list[Any]: The list of parameters for the function.
    """
    args = []
    arg_index = 0
    encountered_star = False
    kwargs = {
        **provided_kwargs,
    }
    for parameter in inspect.signature(fn).parameters.values():
        if parameter.default is not None and parameter.default is not inspect._empty:
            if isinstance(parameter.default, FnDependency):
                dep: Fn = parameter.default.dependency
                try:
                    key_for_fn = dep
                    diagraph[key_for_fn]
                except Exception:
                    raise Exception(
                        f"No function has been set for dep {dep}. Available functions: {diagraph.fns}",
                    ) from None
                if diagraph[key_for_fn].error is not None:
                    raise Exception(f"Error found for {key_for_fn}")
                try:
                    result = diagraph[key_for_fn].result
                    if result == DiagraphStateValueEmpty():
                        raise Exception(f"Result is None for {key_for_fn}")
                    # args.append(diagraph[key_for_fn].result)
                    kwargs[parameter.name] = diagraph[key_for_fn].result
                except Exception as e:
                    raise Exception(
                        f"Failed to get result for {key_for_fn}: {e}",
                    ) from None
            else:
                # This block is for handling the case of: a function has defined a keyword arg,
                # but the user has passed a positional arg for that parameter.
                # Consider:
                # def foo(a, b=1):
                #   ...
                #
                # foo(1, 2)
                #
                # This block of code is to ensure that the above scenario works
                if arg_index <= len(provided_args) - 1:
                    kwargs[parameter.name] = provided_args[arg_index]
                    arg_index += 1

        elif not str(parameter).startswith("*"):
            if encountered_star:
                raise Exception(
                    " ".join(
                        [
                            "Found arguments defined after * args.",
                            "Ensure *args and **kwargs come at the end of the function parameter definitions.",
                        ],
                    ),
                )
            if arg_index > len(provided_args) - 1:
                raise Exception(
                    " ".join(
                        [
                            f'No argument provided for "{parameter.name}" in function {fn.__name__}.',
                            'This indicates you forgot to call ".run()" with sufficient arguments.',
                        ],
                    ),
                )

            args.append(provided_args[arg_index])
            arg_index += 1
        else:
            encountered_star = True

            if arg_index < len(provided_args):
                args += provided_args[arg_index:]
    return args, kwargs
