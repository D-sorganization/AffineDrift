"""Dimensioned examples and finite-difference diagnostics for Geometry Volume I."""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
Field = Callable[[Array], Array]


def _vector(value: Array) -> Array:
    """Require a nonempty finite real vector for the local Euclidean example."""
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or result.size == 0 or not np.all(np.isfinite(result)):
        raise ValueError("Expected a nonempty finite vector.")
    return result


def pendulum_field(
    state: Array, torque: float, parameters: tuple[float, float, float, float]
) -> Array:
    """Return (angular rate, acceleration) for a point mass on a massless rod.

    Parameters are mass [kg], length [m], gravity [m/s^2], and nonnegative
    viscous damping [N m s/rad]. Angle is measured from downward vertical;
    torque is positive in the increasing-angle direction, in N m.
    """
    state = _vector(state)
    values = _vector(np.asarray(parameters))
    if state.shape != (2,) or values.shape != (4,):
        raise ValueError("State and parameter shapes must be (2,) and (4,).")
    mass, length, gravity, damping = values
    if min(mass, length, gravity) <= 0 or damping < 0 or not np.isfinite(torque):
        raise ValueError("Mass, length and gravity must be positive; damping nonnegative.")
    angle, rate = state
    acceleration = torque - mass * gravity * length * np.sin(angle) - damping * rate
    acceleration /= mass * length**2
    return np.array([rate, acceleration])


def central_jacobian(field: Field, state: Array, steps: Array) -> Array:
    """Estimate a rectangular Jacobian using positive coordinate-specific steps.

    This is a floating-point approximation, not proof of differentiability.
    The field must return a fixed-size finite vector throughout the stencil.
    State and steps must use consistent physical units per coordinate.
    """
    state, steps = _vector(state), _vector(steps)
    if steps.shape != state.shape:
        raise ValueError("State and step shapes must match.")
    if np.any(steps <= 0):
        raise ValueError("All coordinate steps must be positive.")
    baseline = _vector(field(state))
    result = np.empty((baseline.size, state.size))
    for index, step in enumerate(steps):
        offset = np.zeros_like(state)
        offset[index] = step
        plus, minus = state + offset, state - offset
        if plus[index] == state[index] or minus[index] == state[index]:
            raise ValueError("Each step must be representable at its state coordinate.")
        upper, lower = _vector(field(plus)), _vector(field(minus))
        if upper.shape != baseline.shape or lower.shape != baseline.shape:
            raise ValueError("Field output shape must be constant across the stencil.")
        result[:, index] = (upper - lower) / (2 * step)
    return result


def residual_table(field: Field, jacobian: Array, state: Array, perturbations: Array) -> Array:
    """Return rows (perturbation norm, residual norm, residual/norm^2).

    Euclidean norms apply to the supplied coordinates; nondimensionalize or
    scale physical coordinates before interpreting mixed-coordinate norms.
    A correct derivative need not give quadratic residuals unless stronger
    regularity holds. Cancellation and derivative error affect small steps.
    """
    state = _vector(state)
    baseline = _vector(field(state))
    jacobian = np.asarray(jacobian, dtype=float)
    perturbations = np.asarray(perturbations, dtype=float)
    if (
        jacobian.shape != (baseline.size, state.size)
        or perturbations.ndim != 2
        or perturbations.shape[1] != state.size
        or len(perturbations) == 0
    ):
        raise ValueError("Jacobian and perturbation shapes must match field and state.")
    if not np.all(np.isfinite(jacobian)) or not np.all(np.isfinite(perturbations)):
        raise ValueError("Jacobian and perturbations must be finite.")
    sizes = np.linalg.norm(perturbations, axis=1)
    if np.any(sizes == 0):
        raise ValueError("Perturbations must be nonzero.")
    residuals = []
    for delta in perturbations:
        changed = _vector(field(state + delta))
        if changed.shape != baseline.shape:
            raise ValueError("Field output shape must remain constant.")
        residuals.append(np.linalg.norm(changed - baseline - jacobian @ delta))
    return np.column_stack((sizes, residuals, np.asarray(residuals) / sizes**2))
