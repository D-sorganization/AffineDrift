"""Pointwise calculations for the contraction chapter, not domain certificates."""

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigvalsh

type Array = NDArray[np.float64]
SYMMETRY_TOLERANCE = 1e-12


def _square_matrix(value: Array, name: str) -> Array:
    """Validate a finite nonempty square array without altering its entries."""
    matrix = np.asarray(value, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a nonempty square matrix")
    if not np.isfinite(matrix).all():
        raise ValueError(f"{name} must have finite entries")
    return matrix


def local_contraction_rate(dynamics: Array, metric: Array, metric_derivative: Array) -> float:
    """Return the sharp signed instantaneous metric-length decay rate.

    The metric derivative is its total derivative along the implemented field.
    A positive result at one point is not a certificate on a region or time
    interval. Uniform metric bounds and appropriate flow/domain assumptions
    remain necessary for the chapter's physical-distance conclusions.
    """
    jacobian = _square_matrix(dynamics, "dynamics")
    ruler = _square_matrix(metric, "metric")
    derivative = _square_matrix(metric_derivative, "metric derivative")
    if ruler.shape != jacobian.shape or derivative.shape != jacobian.shape:
        raise ValueError("all three matrices must have the same shape")
    for matrix in (ruler, derivative):
        if not np.allclose(matrix, matrix.T, atol=SYMMETRY_TOLERANCE, rtol=0):
            raise ValueError("metric and metric derivative must be symmetric")
    if np.linalg.eigvalsh(ruler).min() <= 0:
        raise ValueError("metric must be positive definite")
    residual = derivative + jacobian.T @ ruler + ruler @ jacobian
    return -0.5 * float(eigvalsh(residual, ruler).max())


def vdp_candidate_residual(state: Array, epsilon: float = 0.5, rate: float = 0.3) -> Array:
    """Evaluate the chapter's rejected Van der Pol candidate, with no feedback.

    The fixed candidate is diag(1, 1.2(1 + 1.5 x1²)). Its full-state contraction
    residual has first diagonal entry 2*rate everywhere, disproving feasibility
    for every positive rate independently of any grid or optimizer.
    """
    point = np.asarray(state, dtype=float)
    if point.shape != (2,) or not np.isfinite(point).all():
        raise ValueError("state must have two finite components")
    if not np.isfinite([epsilon, rate]).all() or epsilon <= 0 or rate <= 0:
        raise ValueError("epsilon and rate must be finite and positive")
    position, velocity = point
    velocity_weight, curvature = 1.2, 1.5
    ruler = np.diag([1.0, velocity_weight * (1 + curvature * position**2)])
    derivative = np.diag([0.0, 2 * velocity_weight * curvature * position * velocity])
    jacobian = np.array(
        [[0.0, 1.0], [-1 - 2 * epsilon * position * velocity, epsilon * (1 - position**2)]]
    )
    return np.asarray(derivative + jacobian.T @ ruler + ruler @ jacobian + 2 * rate * ruler)
