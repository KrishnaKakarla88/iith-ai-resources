"""Simple circuit breaker with automatic recovery."""
from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


class CircuitBreakerOpen(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 30.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.failures = 0
        self.opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is None:
            return

        elapsed = time.monotonic() - self.opened_at
        if elapsed >= self.recovery_timeout_seconds:
            # Half-open: allow one call to test recovery.
            return

        remaining = self.recovery_timeout_seconds - elapsed
        raise CircuitBreakerOpen(
            f"Circuit is open. Retry after {remaining:.1f}s."
        )

    def success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.monotonic()


def with_circuit_breaker(breaker: CircuitBreaker):
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            breaker.before_call()
            try:
                result = fn(*args, **kwargs)
            except Exception:
                breaker.failure()
                raise
            breaker.success()
            return result
        return wrapper
    return decorator
