import concurrent.futures
from typing import TYPE_CHECKING, Any

from ..decorators.is_decorated import is_decorated
from ..utils.build_parameters import build_parameters
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .types import ErrorHandler, KeyIdentifier, Result

if TYPE_CHECKING:
    pass


class GraphExecutor:
    # diagraph: Diagraph
    diagraph: Any
    executor: concurrent.futures.ThreadPoolExecutor
    global_error_fn: ErrorHandler | None = None
    seen_keys: set[KeyIdentifier]

    def __init__(
        self,
        # diagraph: Diagraph,
        diagraph: Any,
        starting_nodes: DiagraphNodeGroup,
        input_args,
        input_kwargs,
        max_workers: int,
        global_error_fn: ErrorHandler | None,
    ):
        self.diagraph = diagraph
        self.global_error_fn = global_error_fn
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.seen_keys = set()
        for node in starting_nodes.nodes:
            self.schedule(node, input_args, input_kwargs)
        self.executor.shutdown(wait=True)

    def schedule(self, node: DiagraphNode, input_args, input_kwargs) -> None:
        if node.key not in self.seen_keys:
            self.seen_keys.add(node.key)
            future = self.executor.submit(
                lambda node: self.__execute_node_and_catch_errors__(
                    node,
                    input_args,
                    input_kwargs,
                    rerun_kwargs=None,
                ),
                node,
            )
            concurrent.futures.wait([future])
            for child in node.children:
                if child.__ready__:
                    self.schedule(child, input_args, input_kwargs)

    def __execute_node_and_catch_errors__(
        self,
        node: DiagraphNode,
        input_args: tuple[Any, ...],
        input_kwargs: dict[Any, Any],
        rerun_kwargs: None | dict[Any, Any],
    ) -> None:
        if rerun_kwargs is None:
            rerun_kwargs = {}
        try:
            result = self.__run_node__(node, input_args, input_kwargs)
            self.diagraph.__state__[("result", node.key)] = result
        except Exception as e:
            # TODO: Make this a custom error
            if "Error found for " in str(e):
                return
            if "Failed to get result for " in str(e):
                return
            fn = self.diagraph.fns[node.key]
            fn_error_handler = getattr(fn, "__function_error__", None)

            def rerun(**kwargs: dict[Any, Any]):
                self.__execute_node_and_catch_errors__(
                    node,
                    input_args,
                    input_kwargs,
                    rerun_kwargs=kwargs,
                )
                # TODO: Refactor or remove this
                return node.result

            for err_handler, accepts_fn in [
                (fn_error_handler, False),
                (self.diagraph.error_handler, True),
                (self.global_error_fn, True),
            ]:
                if err_handler:
                    err_handler_args = [e, rerun]
                    if accepts_fn:
                        err_handler_args.append(fn)
                    try:
                        result = err_handler(*err_handler_args, **(rerun_kwargs or {}))
                        self.diagraph.__state__[("result", node.key)] = result
                    except Exception as raised_exception:
                        self.diagraph.__state__[("error", node.key)] = raised_exception
                    return
            # if no error functions are defined, save the error
            self.diagraph.__state__[("error", node.key)] = e

    def __run_node__(
        self,
        node: DiagraphNode,
        provided_args: tuple[Any, ...],
        provided_kwargs: dict[Any, Any],
    ) -> Result:
        """
        Execute a single node in the Diagraph.

        Returns:
            Any: The result of executing the node.
        """
        # If a user has explicitly specified a dependency via an annotation, we hydrate
        # it below.
        # If an argument is _not_ specified as a dependency, pull off the next input arg
        # in order
        fn = self.diagraph.fns[node.key]

        args, kwargs = build_parameters(
            self.diagraph,
            fn,
            provided_args,
            provided_kwargs,
        )

        if self.diagraph.log_handler:
            log_handler = self.diagraph.log_handler
            fn.__diagraph_log__ = lambda event, chunk: log_handler(event, chunk, fn)
        # if self.error_handler:
        #     error_handler = self.error_handler
        #     setattr(fn, "__diagraph_error__", lambda e: error_handler(e, fn))
        fn.__diagraph_llm__ = self.diagraph.llm
        if is_decorated(fn):
            # have we already set a prompt
            return fn(node, *args, **kwargs)

        # if inspect.iscoroutinefunction(fn):
        #     return await fn(*args, **kwargs)
        # else:
        #     return fn(*args, **kwargs)
        return fn(*args, **kwargs)
