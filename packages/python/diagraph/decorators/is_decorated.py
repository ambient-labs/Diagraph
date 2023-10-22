from __future__ import annotations

IS_DECORATED_KEY = "decorated"


def is_decorated(func) -> bool:
    return getattr(func, IS_DECORATED_KEY, False)
