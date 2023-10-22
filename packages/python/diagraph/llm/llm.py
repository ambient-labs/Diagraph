from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from diagraph.classes.types import FunctionLogHandler


class LLM(metaclass=ABCMeta):
    kwargs: dict[str, Any]

    @abstractmethod
    def run(self, _prompt: Any, log: FunctionLogHandler, **kwargs) -> Any:
        ...

    # @abstractmethod
    # async def arun(
    #     self, _prompt: Any, log: FunctionLogHandler, **kwargs
    # ) -> Awaitable[Any]:
    #     ...
