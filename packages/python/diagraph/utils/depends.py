from __future__ import annotations

from typing import Any

from diagraph.classes.types import Fn, KeyIdentifier


def Depends(dependency: Fn) -> Any:
    return FnDependency(dependency)


class FnDependency:
    """
    Dependency injection class.

    Attributes:
    - dependency (Fn): The dependency to be injected.
    """

    dependency: KeyIdentifier

    def __init__(self, dependency: KeyIdentifier):
        """
        Initializes a Depends instance with a given dependency.

        Parameters:
        - dependency (Fn): The dependency to be injected.
        """
        self.dependency = dependency

    def __repr__(self) -> str:
        """
        Returns a string representation of the Depends instance.

        Returns:
        str: A string representation of the Depends instance.
        """
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"
