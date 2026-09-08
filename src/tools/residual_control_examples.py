"""Reproducible scalar teaching examples for residual-aware control."""

import math

import numpy as np
from numpy.typing import NDArray


def residual_step_limit(forcing: float, budget: float, growth: float = 0.0) -> float:
    """Invert a zero-initial-error scalar comparison bound.

    Args:
        forcing: Non-negative upper bound on scaled remainder rate.
        budget: Non-negative local scaled flow-remainder budget.
        growth: Non-negative upper propagator growth rate, in inverse time.

    Returns:
        Largest interval allowed by R'=growth*R+forcing, R(0)=0.
        Zero forcing returns infinity; other validity conditions may still
        require a finite interval. Inputs must be finite and non-negative.
        The result is a floating-point evaluation, not an interval certificate.
    """
    if not all(math.isfinite(value) and value >= 0 for value in (forcing, budget, growth)):
        raise ValueError("forcing, budget, and growth must be finite and non-negative")
    if forcing == 0:
        return math.inf
    limit = budget / forcing
    if growth > 0 and budget > 0:
        scaled = growth * limit
        if scaled > 0 and math.isfinite(scaled):
            limit = math.log1p(scaled) / growth
        elif not math.isfinite(scaled):
            # Evaluate log(1 + growth*budget/forcing) without that overflowing ratio.
            log_scaled = math.log(growth) + math.log(budget) - math.log(forcing)
            limit = float(np.logaddexp(0.0, log_scaled)) / growth
    if not math.isfinite(limit):
        raise ValueError("step limit is not representable as a finite float")
    return limit


def scalar_nonlinear_flow(initial: float, times: NDArray[np.float64]) -> NDArray[np.float64]:
    """Evaluate the dimensionless example x'=x+x^2 before its pole.

    Args:
        initial: Finite non-negative initial state.
        times: Finite non-negative elapsed times in the example's time unit.

    Returns:
        Exact analytical flow evaluated in floating point at each input time.
        The shape of times is preserved. Values at or beyond the finite-time
        pole are rejected; the algebraic continuation is not an ODE solution.
    """
    values = np.asarray(times, dtype=float)
    if not math.isfinite(initial) or initial < 0:
        raise ValueError("initial must be finite and non-negative")
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError("times must be finite and non-negative")
    if initial == 0:
        return np.zeros_like(values)
    # expm1 preserves the initial condition for large initial states at tiny times;
    # decaying exponentials also avoid exp(t) overflow before checking existence.
    denominator = np.exp(-values) + initial * np.expm1(-values)
    if np.any(denominator <= 0):
        raise ValueError("requested time reaches or exceeds the finite-time pole")
    with np.errstate(over="ignore"):
        result = np.asarray(initial / denominator, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError("flow is not representable as finite floats")
    return result
