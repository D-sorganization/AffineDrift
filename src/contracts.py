from collections.abc import Callable


def require(condition: Callable[..., bool], message: str = "Precondition failed"):
    """
    Enforce a precondition on a function.
    """

    def decorator(func):
        """
        Decorator that checks the precondition before calling the function.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper that evaluates the condition and raises ValueError if it fails.
            """
            if not condition(*args, **kwargs):
                raise ValueError(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure(condition: Callable[..., bool], message: str = "Postcondition failed"):
    """
    Enforce a postcondition on a function.
    """

    def decorator(func):
        """
        Decorator that checks the postcondition after calling the function.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper that evaluates the condition on the result and raises RuntimeError if it fails.
            """
            result = func(*args, **kwargs)
            if not condition(result):
                raise RuntimeError(message)
            return result

        return wrapper

    return decorator
