from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class OrderedSet(Generic[T]):
    items: list[T]
    _set: set[T]

    def __init__(self, items: set[T] | None = None) -> None:
        self.items = list(items or {})
        self._set = set()

    def add(self, item: T) -> None:
        if item not in self._set:
            self._set.add(item)
            self.items.append(item)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def pop(self) -> T:
        return self.items.pop()

    def __eq__(self, other) -> bool:
        for item in other:
            if item not in self._set:
                return False
        return True

    def __str__(self):
        return str(self.items)

    def get(self, key) -> T:
        return self.items[key]

    def __getitem__(self, key) -> T:
        return self.items[key]
