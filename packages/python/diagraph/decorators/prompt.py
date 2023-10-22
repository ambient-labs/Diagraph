from __future__ import annotations

import functools
from typing import Any

from ..classes.diagraph_node import DiagraphNode
from ..classes.types import Fn, FunctionErrorHandler, FunctionLogHandler, LogEventName
from ..llm.llm import LLM
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


class UserHandledException(Exception):
    def __init__(self, exception: Exception, raised_exception: Exception) -> None:
        self.exception = exception
        self.raised_exception = raised_exception


__default_llm__: LLM | None = None


def set_default_llm(llm: None | LLM) -> None:
    global __default_llm__
    __default_llm__ = llm


def get_default_llm() -> LLM:
    global __default_llm__
    if __default_llm__ is None:
        __default_llm__ = OpenAI()
    return __default_llm__


def get_if_valid_llm(llm: Any) -> LLM:
    # TODO: Enable this
    # if isinstance(llm, LLM):
    #     return llm
    # else:
    #     raise Exception("The llm passed to @prompt is not a valid LLM object; ensure it is a subclass of LLM")
    return llm


def get_llm(wrapper_fn) -> LLM:
    function_llm = getattr(wrapper_fn, "__function_llm__", None)
    if function_llm is not None:
        return get_if_valid_llm(function_llm)

    diagraph_llm = getattr(wrapper_fn, "__diagraph_llm__", None)
    if diagraph_llm is not None:
        return get_if_valid_llm(diagraph_llm)
    return get_default_llm()


def generate_prompt(func, *args, **kwargs) -> Any:
    # if inspect.iscoroutinefunction(func):
    #     return await func(*args, **kwargs)
    # else:
    #     return func(*args, **kwargs)
    return func(*args, **kwargs)


def decorate(prompt_fn, _func=None, **kwargs):
    def decorator(
        func: Fn,
    ):  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]:
        @functools.wraps(func)
        def wrapper_fn(*args, **kwargs) -> Any:
            return prompt_fn(wrapper_fn, func, *args, **kwargs)

        setattr(wrapper_fn, IS_DECORATED_KEY, True)
        wrapper_fn.__fn__ = func
        for key, value in kwargs.items():
            setattr(wrapper_fn, key, value)
        return wrapper_fn

    if _func is None:
        # Being called with arguments
        return decorator
    setattr(_func, IS_DECORATED_KEY, True)
    _decorator = decorator(_func)
    _decorator.__fn__ = _func
    return _decorator


def prompt(
    _func=None,
    *,
    log: FunctionLogHandler | None = None,
    llm: LLM | None = None,
    error: FunctionErrorHandler | None = None,
):
    def prompt_fn(
        wrapper_fn,
        decorated_fn: Fn,
        node: DiagraphNode,
        *args,
        **kwargs,
    ) -> Any:
        llm = get_llm(wrapper_fn)
        diagraph_log = getattr(wrapper_fn, "__diagraph_log__", None)

        def _log(event: LogEventName, chunk: dict | None) -> None:
            if log:
                log(event, chunk)
            elif diagraph_log:
                diagraph_log(event, chunk)

        prompt = None
        try:
            prompt = node.prompt
        except Exception:
            pass
        if prompt is None:
            node.diagraph.__state__[("prompt", node.key)] = generate_prompt(
                decorated_fn,
                *args,
                **kwargs,
            )

        return llm.run(node.prompt, log=_log)

    return decorate(prompt_fn, _func, __function_llm__=llm, __function_error__=error)
