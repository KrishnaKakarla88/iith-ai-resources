"""Small synchronous retry helper with exponential backoff."""
from __future__ import annotations

import random
import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    base_delay_seconds: float = 0.25,
):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts:
                        raise
                    delay = base_delay_seconds * (2 ** (attempt - 1))
                    delay += random.uniform(0, 0.1)
                    time.sleep(delay)
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator
