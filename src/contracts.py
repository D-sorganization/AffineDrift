from collections.abc import Callable


def require(condition: Callable[..., bool], message: str = "Precondition failed"):
    """
    Enforces a precondition on the decorated function.
    """

    def decorator(func):
        """Decorator that wraps the function with precondition checks."""

        def wrapper(*args, **kwargs):
            """Wrapper function that executes the precondition."""
            if not condition(*args, **kwargs):
                raise ValueError(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure(condition: Callable[..., bool], message: str = "Postcondition failed"):
    """
    Enforces a postcondition on the decorated function's result.
    """

    def decorator(func):
        """Decorator that wraps the function with postcondition checks."""

        def wrapper(*args, **kwargs):
            """Wrapper function that executes the postcondition."""
            result = func(*args, **kwargs)
            if not condition(result):
                raise RuntimeError(message)
            return result

        return wrapper

    return decorator
