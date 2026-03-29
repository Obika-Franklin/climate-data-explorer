"""Safety and guardrail utilities."""

from __future__ import annotations

from typing import Any, Callable

MAX_ITERATIONS = 3


def bounded_run(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a function with a unified error envelope."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        return {
            "status": "error",
            "message": str(exc),
        }
