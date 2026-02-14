"""Numeric and array validation contract helpers.

This module provides convenience validators for common numeric assertions
used throughout the AffineDrift platform. All validators delegate to the
core ``require()`` primitive from ``definitions``.
"""

from __future__ import annotations

from typing import Any

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover
    np = None  # type: ignore[assignment]

from src.core.contracts.definitions import require


def check_finite_array(arr: np.ndarray[Any, Any], name: str = "array") -> None:
    """Assert that a numpy array contains only finite values."""
    require(
        bool(np.all(np.isfinite(arr))),
        f"{name} must contain only finite values (no NaN or Inf)",
        arr,
    )


def check_positive(value: float, name: str = "value") -> None:
    """Assert that a numeric value is strictly positive."""
    require(value > 0, f"{name} must be positive", value)


def check_non_negative(value: float, name: str = "value") -> None:
    """Assert that a numeric value is non-negative."""
    require(value >= 0, f"{name} must be non-negative", value)


def check_range(
    value: float,
    low: float,
    high: float,
    name: str = "value",
) -> None:
    """Assert that a numeric value falls within [low, high]."""
    require(low <= value <= high, f"{name} must be in [{low}, {high}]", value)


def check_shape(
    arr: np.ndarray[Any, Any],
    expected_shape: tuple[int, ...],
    name: str = "array",
) -> None:
    """Assert that a numpy array has the expected shape."""
    require(
        arr.shape == expected_shape,
        f"{name} must have shape {expected_shape}",
        arr,
    )
