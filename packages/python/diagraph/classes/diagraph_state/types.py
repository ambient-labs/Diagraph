from typing import Any

from ..types import Fn

StateArgs = tuple[Any, ...]
StateKey = tuple[str | Fn, ...] | str
StateValue = Any
