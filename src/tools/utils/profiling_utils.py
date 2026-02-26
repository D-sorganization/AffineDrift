"""Profiling utilities for performance analysis.

This module provides tools to measure and analyze the performance of
functions and code blocks.
"""

import functools
import timeit
from collections.abc import Callable
from typing import Any

from .logging_utils import setup_logging

logger = setup_logging(__name__)


def profile_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure and log the execution time of a function.

    Args:
        func: The function to profile.

    Returns:
        The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = timeit.default_timer()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = timeit.default_timer()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} took {execution_time:.4f} seconds to execute.")

    return wrapper
