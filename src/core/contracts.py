"""Design by Contract (DbC) enforcement for the AffineDrift platform.

This module provides lightweight helpers and decorators for enforcing
pre-conditions, post-conditions, and invariants at runtime.

Enforcement Levels (controlled via ``DBC_LEVEL`` environment variable):
  - ``enforce`` (default): Raise ``ContractViolationError`` on failure.
  - ``warn``: Log violations at WARNING level but do not raise.
  - ``off``: Skip all contract checks (maximum performance).

Usage (function-call style):

    from src.core.contracts import require, ensure, check_finite_array

    def compute_trajectory(x0: np.ndarray, u: np.ndarray) -> np.ndarray:
        require(x0.size > 0, "initial state must not be empty")
        check_finite_array(x0, "x0")
        result = _integrate(x0, u)
        ensure(check_finite_array(result, "result"))
        return result

Usage (decorator style):

    from src.core.contracts import precondition, postcondition

    @precondition(lambda x, u: x.size > 0, "state must not be empty")
    @postcondition(lambda r: np.all(np.isfinite(r)), "result must be finite")
    def step(x: np.ndarray, u: np.ndarray) -> np.ndarray:
        ...

Usage (class invariants):

    from src.core.contracts import ContractChecker

    class ResidualMonitor(ContractChecker):
        def _get_invariants(self):
            return [
                (lambda: self.eps_warning > 0, "eps_warning must be positive"),
                (lambda: self.eps_critical > self.eps_warning,
                 "eps_critical must exceed eps_warning"),
            ]

Reference: Bertrand Meyer, "Object-Oriented Software Construction" (1997).
"""

from __future__ import annotations

import enum
import functools
import logging
import os
from collections.abc import Callable
from typing import Any, TypeVar, cast

import numpy as np

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# ─── Contract Enforcement Level ────────────────────────────────


class ContractLevel(enum.Enum):
    """Tri-state enforcement level for Design by Contract checks."""

    OFF = "off"
    WARN = "warn"
    ENFORCE = "enforce"


def _resolve_contract_level() -> ContractLevel:
    """Determine the contract level from environment."""
    env_val = os.environ.get("DBC_LEVEL", "").lower().strip()
    if env_val in ("off", "warn", "enforce"):
        return ContractLevel(env_val)
    return ContractLevel.ENFORCE if __debug__ else ContractLevel.OFF


DBC_LEVEL: ContractLevel = _resolve_contract_level()
CONTRACTS_ENABLED = DBC_LEVEL != ContractLevel.OFF


def set_contract_level(level: ContractLevel) -> None:
    """Set the global contract enforcement level at runtime."""
    global DBC_LEVEL, CONTRACTS_ENABLED  # noqa: PLW0603
    DBC_LEVEL = level
    CONTRACTS_ENABLED = level != ContractLevel.OFF
    logger.info("Contract enforcement level set to %s", level.value)


def get_contract_level() -> ContractLevel:
    """Return the current global contract enforcement level."""
    return DBC_LEVEL


# ─── Exception Hierarchy ───────────────────────────────────────


class ContractViolationError(AssertionError, ValueError):
    """Base exception for contract violations."""

    def __init__(
        self,
        condition_type: str,
        message: str,
        value: Any = None,
    ) -> None:
        self.condition_type = condition_type
        self.message = message
        self.value = value
        detail = f"[DbC {condition_type}] {message}"
        if value is not None:
            if isinstance(value, np.ndarray):
                detail += f" (shape={value.shape}, dtype={value.dtype})"
            else:
                detail += f" (got: {value!r})"
        super().__init__(detail)


class PreconditionError(ContractViolationError):
    """Raised when a pre-condition is violated."""

    def __init__(self, message: str, value: Any = None) -> None:
        super().__init__("pre-condition", message, value)


class PostconditionError(ContractViolationError):
    """Raised when a post-condition is violated."""

    def __init__(self, message: str, value: Any = None) -> None:
        super().__init__("post-condition", message, value)


class InvariantError(ContractViolationError):
    """Raised when a class or loop invariant is violated."""

    def __init__(self, message: str, value: Any = None) -> None:
        super().__init__("invariant", message, value)


# ─── Core Contract Primitives ─────────────────────────────────


def _handle_violation(
    condition_type: str,
    message: str,
    value: Any = None,
) -> None:
    """Handle a contract violation according to the current DBC_LEVEL."""
    if DBC_LEVEL == ContractLevel.ENFORCE:
        raise ContractViolationError(condition_type, message, value)
    elif DBC_LEVEL == ContractLevel.WARN:
        detail = f"[DbC {condition_type}] {message}"
        if value is not None:
            detail += f" (got: {value!r})"
        logger.warning(detail)


def require(condition: bool, message: str, value: Any = None) -> None:
    """Assert a pre-condition at function entry."""
    if DBC_LEVEL == ContractLevel.OFF:
        return
    if not condition:
        _handle_violation("pre-condition", message, value)


def ensure(condition: bool, message: str, value: Any = None) -> None:
    """Assert a post-condition before function return."""
    if DBC_LEVEL == ContractLevel.OFF:
        return
    if not condition:
        _handle_violation("post-condition", message, value)


def invariant(condition: bool, message: str, value: Any = None) -> None:
    """Assert a class or loop invariant."""
    if DBC_LEVEL == ContractLevel.OFF:
        return
    if not condition:
        _handle_violation("invariant", message, value)


# ─── Decorator-Based Contracts ─────────────────────────────────


def precondition(
    condition: Callable[..., bool],
    message: str = "Precondition failed",
) -> Callable[[F], F]:
    """Decorator to enforce a precondition on a function or method."""

    def decorator(func: F) -> F:
        if DBC_LEVEL == ContractLevel.OFF:
            return func

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = condition(*args, **kwargs)
            except (TypeError, ValueError) as exc:
                _handle_violation(
                    "pre-condition",
                    f"Failed to evaluate precondition for {func.__qualname__}: {exc}",
                )
                return func(*args, **kwargs)

            if not result:
                _handle_violation("pre-condition", message)

            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def postcondition(
    condition: Callable[[Any], bool],
    message: str = "Postcondition failed",
) -> Callable[[F], F]:
    """Decorator to enforce a postcondition on a function's return value."""

    def decorator(func: F) -> F:
        if DBC_LEVEL == ContractLevel.OFF:
            return func

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            try:
                check = condition(result)
            except (TypeError, ValueError) as exc:
                _handle_violation(
                    "post-condition",
                    f"Failed to evaluate postcondition for {func.__qualname__}: {exc}",
                )
                return result

            if not check:
                _handle_violation("post-condition", message, result)

            return result

        return cast(F, wrapper)

    return decorator


# ─── Class Invariant Mixin ─────────────────────────────────────


class ContractChecker:
    """Mixin providing class invariant checking.

    Subclasses override ``_get_invariants()`` to define their invariants.
    """

    def _get_invariants(self) -> list[tuple[Callable[[], bool], str]]:
        """Return list of (condition, message) tuples for invariants."""
        return []

    def verify_invariants(self) -> bool:
        """Verify all class invariants hold."""
        if DBC_LEVEL == ContractLevel.OFF:
            return True

        for condition_fn, message in self._get_invariants():
            try:
                if not condition_fn():
                    if DBC_LEVEL == ContractLevel.ENFORCE:
                        raise InvariantError(f"{self.__class__.__name__}: {message}")
                    else:
                        logger.warning(
                            "[DbC invariant] %s: %s",
                            self.__class__.__name__,
                            message,
                        )
            except InvariantError:
                raise
            except (RuntimeError, TypeError, ValueError) as exc:
                if DBC_LEVEL == ContractLevel.ENFORCE:
                    raise InvariantError(
                        f"{self.__class__.__name__}: Failed to evaluate invariant: {exc}"
                    ) from exc

        return True


def invariant_checked[F: Callable[..., Any]](func: F) -> F:
    """Decorator to check class invariants after method execution."""
    if DBC_LEVEL == ContractLevel.OFF:
        return func

    @functools.wraps(func)
    def wrapper(self: ContractChecker, *args: Any, **kwargs: Any) -> Any:
        result = func(self, *args, **kwargs)
        self.verify_invariants()
        return result

    return cast(F, wrapper)


# ─── Numeric/Array Contract Helpers ────────────────────────────


def check_finite_array(arr: np.ndarray, name: str = "array") -> None:
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
    arr: np.ndarray,
    expected_shape: tuple[int, ...],
    name: str = "array",
) -> None:
    """Assert that a numpy array has the expected shape."""
    require(
        arr.shape == expected_shape,
        f"{name} must have shape {expected_shape}",
        arr,
    )
