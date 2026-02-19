"""Utilities for performance profiling."""

import functools
import logging
import timeit

logger = logging.getLogger(__name__)


def profile_execution_time(func):
    """Decorator to profile execution time of a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function to measure execution time."""
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        logger.info("Execution time of %s: %.4f seconds", func.__name__, end_time - start_time)
        return result

    return wrapper
