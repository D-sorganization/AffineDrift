"""Shared numerical test helpers for AffineDrift.

This module provides assertion utilities commonly needed when testing
scientific / control-theory code:

- closeness comparisons with diagnostic messages
- conservation checks (mass, energy, element balances)
- monotonicity verification
- finiteness guards
- positive-definiteness checks
- Lyapunov stability assertions

Design-by-Contract
-------------------
Every public function states its preconditions and raises ``ValueError``
for violated preconditions or ``AssertionError`` for violated postconditions
(i.e. a failed test assertion).
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import numpy.typing as npt


# ---------------------------------------------------------------------------
# Closeness
# ---------------------------------------------------------------------------

def assert_close(
    actual: float,
    expected: float,
    rtol: float = 1e-7,
    atol: float = 0.0,
    label: str = "value",
) -> None:
    """Assert *actual* is close to *expected* with a diagnostic message.

    Preconditions:
        - *rtol* >= 0
        - *atol* >= 0

    Uses the same formula as :func:`numpy.isclose`::

        |actual - expected| <= atol + rtol * |expected|
    """
    if rtol < 0:
        raise ValueError(f"rtol must be >= 0, got {rtol}")
    if atol < 0:
        raise ValueError(f"atol must be >= 0, got {atol}")

    diff = abs(actual - expected)
    tolerance = atol + rtol * abs(expected)
    if diff > tolerance:
        raise AssertionError(
            f"{label}: expected {expected}, got {actual} "
            f"(diff={diff:.3e}, tol={tolerance:.3e}, rtol={rtol}, atol={atol})"
        )


# ---------------------------------------------------------------------------
# Conservation
# ---------------------------------------------------------------------------

def assert_conserved(
    before: float,
    after: float,
    quantity_name: str,
    rtol: float = 1e-6,
) -> None:
    """Assert a conserved quantity has not drifted.

    Preconditions:
        - *rtol* >= 0

    This is a convenience wrapper around :func:`assert_close` with a
    domain-specific error message suitable for mass / energy / element
    conservation checks.
    """
    if rtol < 0:
        raise ValueError(f"rtol must be >= 0, got {rtol}")

    assert_close(
        after,
        before,
        rtol=rtol,
        atol=0.0,
        label=f"Conservation of {quantity_name}",
    )


# ---------------------------------------------------------------------------
# Monotonicity
# ---------------------------------------------------------------------------

def assert_monotonic(
    values: Sequence[float],
    increasing: bool = True,
    strict: bool = False,
    label: str = "sequence",
) -> None:
    """Assert that *values* are monotonically ordered.

    Preconditions:
        - len(values) >= 2

    Parameters
    ----------
    values : sequence of float
        The sequence to check.
    increasing : bool
        If ``True`` (default), check non-decreasing (or strictly increasing
        when *strict* is ``True``). If ``False``, check non-increasing (or
        strictly decreasing).
    strict : bool
        If ``True``, disallow equal consecutive values.
    label : str
        Human-readable label for error messages.
    """
    if len(values) < 2:
        raise ValueError(
            f"Need at least 2 values to check monotonicity, got {len(values)}"
        )

    direction = "increasing" if increasing else "decreasing"
    strictness = "strictly " if strict else ""

    for i in range(len(values) - 1):
        a, b = values[i], values[i + 1]
        if increasing:
            ok = (a < b) if strict else (a <= b)
        else:
            ok = (a > b) if strict else (a >= b)

        if not ok:
            raise AssertionError(
                f"{label} is not {strictness}{direction} "
                f"at index {i}: {a} -> {b}"
            )


# ---------------------------------------------------------------------------
# Finiteness
# ---------------------------------------------------------------------------

def is_finite(value: float) -> bool:
    """Return ``True`` if *value* is neither NaN nor Inf.

    Works for plain floats and numpy scalars.
    """
    return bool(math.isfinite(float(value)))


def assert_all_finite(values: Sequence[float], label: str = "values") -> None:
    """Assert every element of *values* is finite.

    Preconditions:
        - *values* is non-empty
    """
    if len(values) == 0:
        raise ValueError(f"{label}: cannot check finiteness of empty sequence")

    for i, v in enumerate(values):
        if not is_finite(v):
            raise AssertionError(
                f"{label}[{i}] is not finite: {v}"
            )


# ---------------------------------------------------------------------------
# Positive-definiteness
# ---------------------------------------------------------------------------

def assert_positive_definite(
    matrix: npt.ArrayLike,
    label: str = "matrix",
) -> None:
    """Assert that *matrix* is symmetric positive-definite.

    Preconditions:
        - *matrix* is 2-D and square
        - *matrix* is real-valued

    Checks:
        1. Symmetry (within floating-point tolerance)
        2. All eigenvalues > 0
    """
    mat = np.asarray(matrix, dtype=float)
    if mat.ndim != 2:
        raise ValueError(f"{label} must be 2-D, got {mat.ndim}-D")
    if mat.shape[0] != mat.shape[1]:
        raise ValueError(
            f"{label} must be square, got shape {mat.shape}"
        )

    # Symmetry
    if not np.allclose(mat, mat.T):
        raise AssertionError(f"{label} is not symmetric")

    # Eigenvalues
    eigenvalues = np.linalg.eigvalsh(mat)
    min_eig = float(eigenvalues.min())
    if min_eig <= 0:
        raise AssertionError(
            f"{label} is not positive definite "
            f"(smallest eigenvalue = {min_eig:.3e})"
        )


# ---------------------------------------------------------------------------
# Lyapunov stability
# ---------------------------------------------------------------------------

def assert_lyapunov_stable(
    V_values: Sequence[float],
    label: str = "Lyapunov function",
    rtol: float = 1e-12,
) -> None:
    """Assert Lyapunov stability: V(t) should be non-increasing.

    A Lyapunov function V must satisfy:
        1. V(t) >= 0 for all t
        2. V(t+1) <= V(t) for all t  (non-increasing)

    Small numerical increases up to *rtol* * V(t) are tolerated.

    Preconditions:
        - len(V_values) >= 2
        - rtol >= 0
    """
    if len(V_values) < 2:
        raise ValueError(
            f"Need at least 2 values to check Lyapunov stability, "
            f"got {len(V_values)}"
        )
    if rtol < 0:
        raise ValueError(f"rtol must be >= 0, got {rtol}")

    for i, v in enumerate(V_values):
        if v < 0:
            raise AssertionError(
                f"{label}[{i}] = {v} is negative (Lyapunov functions must be non-negative)"
            )

    for i in range(len(V_values) - 1):
        v_now = V_values[i]
        v_next = V_values[i + 1]
        # Allow tiny increases due to floating-point noise
        if v_next > v_now * (1 + rtol) + rtol:
            raise AssertionError(
                f"{label} increased at step {i}: "
                f"V[{i}]={v_now:.6e} -> V[{i+1}]={v_next:.6e} "
                f"(increase={v_next - v_now:.3e})"
            )
