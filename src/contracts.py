from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def require(
    condition: Callable[..., bool], message: str = "Precondition failed"
) -> Callable[[F], F]:
    """Decorator to enforce a precondition before executing the function."""

    def decorator(func: F) -> F:
        """The actual decorator returned by require."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper that runs the precondition check."""
            if not condition(*args, **kwargs):
                raise ValueError(message)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def ensure(
    condition: Callable[..., bool], message: str = "Postcondition failed"
) -> Callable[[F], F]:
    """Decorator to enforce a postcondition after executing the function."""

    def decorator(func: F) -> F:
        """The actual decorator returned by ensure."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper that runs the postcondition check."""
            result = func(*args, **kwargs)
            if not condition(result):
                raise RuntimeError(message)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
