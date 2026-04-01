from collections.abc import Callable


def require(condition: Callable[..., bool], message: str = "Precondition failed"):
    """
    Enforce a precondition on a function's arguments.

    Args:
        condition: A callable that returns True if the precondition is met.
        message: The error message to raise if the precondition fails.
    """

    def decorator(func):
        """Apply the precondition wrapper to the function."""

        def wrapper(*args, **kwargs):
            """Execute the precondition check before the function."""
            if not condition(*args, **kwargs):
                raise ValueError(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure(condition: Callable[..., bool], message: str = "Postcondition failed"):
    """
    Enforce a postcondition on a function's return value.

    Args:
        condition: A callable that returns True if the postcondition is met.
        message: The error message to raise if the postcondition fails.
    """

    def decorator(func):
        """Apply the postcondition wrapper to the function."""

        def wrapper(*args, **kwargs):
            """Execute the postcondition check after the function returns."""
            result = func(*args, **kwargs)
            if not condition(result):
                raise RuntimeError(message)
            return result

        return wrapper

    return decorator
