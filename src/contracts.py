from __future__ import annotations

from collections.abc import Callable
from functools import wraps


def require[**P, R](
    condition: Callable[P, bool], message: str = "Precondition failed"
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Enforce a precondition on a function's arguments.

    Args:
        condition: A callable that returns True if the precondition is met.
        message: The error message to raise if the precondition fails.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Apply the precondition wrapper to the function."""

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Execute the precondition check before the function."""
            if not condition(*args, **kwargs):
                raise ValueError(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure[**P, R](
    condition: Callable[[R], bool], message: str = "Postcondition failed"
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Enforce a postcondition on a function's return value.

    Args:
        condition: A callable that returns True if the postcondition is met.
        message: The error message to raise if the postcondition fails.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Apply the postcondition wrapper to the function."""

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Execute the postcondition check after the function returns."""
            result = func(*args, **kwargs)
            if not condition(result):
                raise RuntimeError(message)
            return result

        return wrapper

    return decorator
