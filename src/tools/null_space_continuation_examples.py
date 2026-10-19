"""Solution-manifold continuation examples for the null-space exploration section (P6).

Local statements only. Where the Jacobian ``DF(u)`` has full row rank the zero set of ``F`` is,
by the implicit function theorem, a manifold near ``u`` whose tangent space is ``null(DF(u))``.
A tangent predictor ``u + h t`` leaves a residual of order ``h**2``; a minimum-norm Gauss-Newton
corrector then converges locally and quadratically. The corrector is a descent heuristic, not a
nearest-point projection, and every claim fails where the Jacobian drops rank.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

Vector = NDArray[np.float64]
Matrix = NDArray[np.float64]
ResidualFn = Callable[[Vector], Vector]
JacobianFn = Callable[[Vector], Matrix]

RANK_RTOL = 1e-10  # relative singular-value cutoff for numerical rank
SLOPE_STEPS = (0.4, 0.2, 0.1, 0.05, 0.025, 0.0125)  # step sizes for the log-log slope fit
COUNTEREXAMPLE_POINT = (0.0, 1.0)  # off-manifold start for the nearest-point counterexample
CORRECTOR_TOL = 1e-14  # residual tolerance used by the section builder
CORRECTOR_MAX_ITER = 50
FOLD_TRACE_STEPS = 14
FOLD_TRACE_H = 0.25
QUADRATIC_RATIO_FLOOR = 1e-6  # ignore residuals below this when forming r_{k+1}/r_k**2


class RankChangeError(ValueError):
    """The Jacobian lost full row rank, so the local manifold chart is not available."""


@dataclass(frozen=True)
class StepResult:
    """Outcome of one predictor-corrector step.

    Attributes:
        point: Corrected point with residual norm at most ``tol``.
        iterations: Number of Gauss-Newton corrections applied.
        residual_history: Residual norms, predictor first; length ``iterations + 1``.
    """

    point: Vector
    iterations: int
    residual_history: tuple[float, ...]


def circle_constraint(u: Vector) -> Vector:
    """Return ``F(u) = ||u||^2 - 1``."""
    return np.array([float(u @ u) - 1.0])


def circle_jacobian(u: Vector) -> Matrix:
    """Return ``DF(u) = 2 u^T`` (1 x n)."""
    return np.asarray(2.0 * u, dtype=float).reshape(1, -1)


def fold_constraint(u: Vector) -> Vector:
    """Return ``F(u) = u_2 - u_1^2``; ``u_2`` has a turning point at ``u_1 = 0``."""
    return np.array([u[1] - u[0] ** 2])


def fold_jacobian(u: Vector) -> Matrix:
    """Return ``DF(u) = [-2 u_1, 1]``; full rank everywhere."""
    return np.array([[-2.0 * u[0], 1.0]])


def rank_drop_constraint(u: Vector) -> Vector:
    """Return ``F(u) = u_1 u_2``, whose zero set is the two coordinate axes."""
    return np.array([u[0] * u[1]])


def rank_drop_jacobian(u: Vector) -> Matrix:
    """Return ``DF(u) = [u_2, u_1]``, which vanishes at the origin (rank 0 < 1)."""
    return np.array([[u[1], u[0]]])


def _as_vector(value: Any, name: str) -> Vector:
    """Validate a finite 1-D float vector."""
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a numpy array, got {type(value).__name__}")
    if value.ndim != 1 or value.size == 0:
        raise ValueError(f"{name} must be a non-empty 1-D array, got shape {value.shape}")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be finite")
    return np.asarray(value, dtype=float)


def _validate_jacobian(jac: Any, rtol: float) -> Matrix:
    """Validate a finite 2-D Jacobian and a non-negative relative tolerance."""
    if not isinstance(jac, np.ndarray):
        raise TypeError(f"jac must be a numpy array, got {type(jac).__name__}")
    if jac.ndim != 2 or jac.size == 0:
        raise ValueError(f"jac must be a non-empty 2-D array, got shape {jac.shape}")
    if not np.all(np.isfinite(jac)):
        raise ValueError("jac must be finite")
    if not np.isfinite(rtol) or rtol < 0:
        raise ValueError(f"rtol must be finite and non-negative, got {rtol}")
    return np.asarray(jac, dtype=float)


def _svd_rank(jac: Matrix, rtol: float) -> tuple[int, Matrix]:
    """Return numerical rank and the right singular vectors ``Vt`` of ``jac``."""
    _, sigma, vt = np.linalg.svd(jac, full_matrices=True)
    cutoff = rtol * (sigma[0] if sigma.size else 0.0)
    rank = int(np.sum(sigma > cutoff)) if sigma.size and sigma[0] > 0 else 0
    return rank, vt


def jacobian_rank(jac: Matrix, *, rtol: float) -> int:
    """Numerical rank of ``jac``: singular values above ``rtol * sigma_max``.

    Preconditions: ``jac`` is a finite non-empty 2-D array and ``rtol >= 0``.
    Postconditions: result is in ``[0, min(jac.shape)]``; the zero matrix has rank 0.
    """
    return _svd_rank(_validate_jacobian(jac, rtol), rtol)[0]


def local_tangent_basis(jac: Matrix, *, rtol: float) -> Matrix:
    """Orthonormal basis of ``null(jac)`` as columns (the local tangent space).

    Preconditions: ``jac`` is a finite non-empty 2-D array and ``rtol >= 0``.
    Postconditions: shape ``(n, n - rank)``; ``jac @ basis`` is zero to rounding and
    ``basis.T @ basis`` is the identity. At a rank drop the basis is larger than the
    generic fibre dimension, which is how the drop is reported to the caller.
    """
    matrix = _validate_jacobian(jac, rtol)
    rank, vt = _svd_rank(matrix, rtol)
    return np.asarray(vt[rank:].T, dtype=float)


def _unit_tangent(jac: Matrix, direction: Vector) -> Vector:
    """Project ``direction`` on the tangent space and normalise it."""
    basis = local_tangent_basis(jac, rtol=RANK_RTOL)
    projected = basis @ (basis.T @ direction)
    length = float(np.linalg.norm(projected))
    if length <= RANK_RTOL * max(float(np.linalg.norm(direction)), 1.0):
        raise ValueError("direction has no component along the tangent space")
    return np.asarray(projected / length, dtype=float)


def _full_rank_jacobian(residual: ResidualFn, jacobian: JacobianFn, u: Vector) -> Matrix:
    """Evaluate ``DF(u)`` and require full row rank (a regular point)."""
    jac = np.asarray(jacobian(u), dtype=float)
    rows = int(np.atleast_1d(residual(u)).size)
    rank = jacobian_rank(jac, rtol=RANK_RTOL)
    if rank < rows:
        raise RankChangeError(
            f"Jacobian rank {rank} < {rows} equations at u={u.tolist()}: "
            "the implicit-function chart does not exist here"
        )
    return jac


def _check_step_arguments(h: float, tol: float, max_iter: int) -> None:
    """Validate scalar step arguments."""
    if not np.isfinite(h):
        raise ValueError(f"h must be finite, got {h}")
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError(f"tol must be finite and positive, got {tol}")
    if isinstance(max_iter, bool) or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError(f"max_iter must be an int >= 1, got {max_iter!r}")


def _gauss_newton_correct(
    residual: ResidualFn, jacobian: JacobianFn, start: Vector, tol: float, max_iter: int
) -> StepResult:
    """Minimum-norm Gauss-Newton iteration ``u <- u - DF^+ F`` with rank checks."""
    point = start.copy()
    history: list[float] = []
    for iteration in range(max_iter + 1):
        value = np.asarray(residual(point), dtype=float)
        jac = _full_rank_jacobian(residual, jacobian, point)
        history.append(float(np.linalg.norm(value)))
        if history[-1] <= tol:
            return StepResult(point, iteration, tuple(history))
        if iteration < max_iter:
            point = point + np.linalg.lstsq(jac, -value, rcond=None)[0]
    raise RuntimeError(f"corrector did not converge to tol={tol} in {max_iter} iterations")


def _predict(
    residual: ResidualFn, jacobian: JacobianFn, u: Vector, direction: Vector, h: float
) -> tuple[Vector, Vector]:
    """Validate inputs and return ``(unit tangent at u, predictor u + h t)``."""
    start = _as_vector(u, "u")
    heading = _as_vector(direction, "direction")
    if heading.size != start.size:
        raise ValueError(f"direction length {heading.size} != u length {start.size}")
    tangent = _unit_tangent(_full_rank_jacobian(residual, jacobian, start), heading)
    return tangent, start + h * tangent


def tangent_step_residual(
    residual: ResidualFn, jacobian: JacobianFn, u: Vector, direction: Vector, h: float
) -> float:
    """Norm of ``F(u + h t)`` for the unit tangent ``t`` nearest ``direction``.

    Preconditions: ``u`` lies on the manifold; ``DF(u)`` has full row rank; ``h`` finite.
    Postconditions: ``O(h**2)`` as ``h -> 0`` for a twice-differentiable ``F``.
    """
    _, predicted = _predict(residual, jacobian, u, direction, h)
    return float(np.linalg.norm(residual(predicted)))


def predictor_corrector_step(
    residual: ResidualFn,
    jacobian: JacobianFn,
    u: Vector,
    direction: Vector,
    h: float,
    *,
    tol: float,
    max_iter: int,
) -> StepResult:
    """One tangent-predictor, minimum-norm Gauss-Newton-corrector step.

    Preconditions: ``u`` and ``direction`` are finite 1-D arrays of equal length; ``h`` is
    finite; ``tol > 0``; ``max_iter >= 1``; ``direction`` has a component along ``null(DF(u))``;
    ``DF`` has full row rank at ``u``.
    Postconditions: the returned point has residual norm ``<= tol`` and
    ``iterations == len(residual_history) - 1``. Raises ``RankChangeError`` when the
    Jacobian loses full row rank at ``u``, at the predictor or at any corrector iterate,
    and ``RuntimeError`` when the corrector does not reach ``tol`` within ``max_iter``.
    The correction is minimum-norm per step, so the limit is generally not the nearest
    manifold point.
    """
    _check_step_arguments(h, tol, max_iter)
    _, predicted = _predict(residual, jacobian, u, direction, h)
    return _gauss_newton_correct(residual, jacobian, predicted, tol, max_iter)


def trace_manifold(
    residual: ResidualFn,
    jacobian: JacobianFn,
    u0: Vector,
    direction: Vector,
    h: float,
    *,
    n_steps: int,
    tol: float,
    max_iter: int,
) -> Matrix:
    """Pseudo-arclength continuation: ``n_steps`` predictor-corrector steps from ``u0``.

    Each new heading is the previous heading projected onto the new tangent space, so the
    trace passes through coordinate turning points (e.g. the fold vertex) without reversing.

    Preconditions: as ``predictor_corrector_step`` plus ``n_steps >= 1``; ``u0`` on the manifold.
    Postconditions: array of shape ``(n_steps + 1, n)`` whose first row is ``u0``.
    """
    if isinstance(n_steps, bool) or not isinstance(n_steps, int) or n_steps < 1:
        raise ValueError(f"n_steps must be an int >= 1, got {n_steps!r}")
    points = [_as_vector(u0, "u0")]
    heading = _as_vector(direction, "direction")
    for _ in range(n_steps):
        result = predictor_corrector_step(
            residual, jacobian, points[-1], heading, h, tol=tol, max_iter=max_iter
        )
        points.append(result.point)
        heading = _unit_tangent(_full_rank_jacobian(residual, jacobian, result.point), heading)
    return np.vstack(points)


def min_norm_correction_limit(point: Vector) -> Vector:
    """Gauss-Newton limit on the fold from an off-manifold ``point`` (no predictor)."""
    return _gauss_newton_correct(
        fold_constraint,
        fold_jacobian,
        _as_vector(point, "point"),
        CORRECTOR_TOL,
        CORRECTOR_MAX_ITER,
    ).point


def nearest_point_on_fold(point: Vector) -> Vector:
    """Exact nearest point on ``u_2 = u_1^2`` to ``point`` (real root of the stationarity polynomial).

    Minimising ``(x - p_1)^2 + (x^2 - p_2)^2`` gives ``2 x^3 + (1 - 2 p_2) x - p_1 = 0``; the
    real root with least distance is returned.
    """
    p = _as_vector(point, "point")
    roots = np.roots([2.0, 0.0, 1.0 - 2.0 * p[1], -p[0]])
    real = roots[np.abs(roots.imag) < 1e-9].real
    candidates = np.column_stack([real, real**2])
    return np.asarray(candidates[np.argmin(np.linalg.norm(candidates - p, axis=1))], dtype=float)


def _fit_slope(steps: tuple[float, ...], values: list[float]) -> float:
    """Least-squares slope of ``log(values)`` against ``log(steps)``."""
    return float(np.polyfit(np.log(np.asarray(steps)), np.log(np.asarray(values)), 1)[0])


def _tangent_residual_entry(
    residual: ResidualFn, jacobian: JacobianFn, u: Vector, direction: Vector
) -> dict[str, Any]:
    """Tangent-step residuals over ``SLOPE_STEPS`` and their fitted log-log slope."""
    values = [tangent_step_residual(residual, jacobian, u, direction, h) for h in SLOPE_STEPS]
    return {
        "steps": list(SLOPE_STEPS),
        "residuals": values,
        "fitted_slope": _fit_slope(SLOPE_STEPS, values),
    }


def _quadratic_entry() -> dict[str, Any]:
    """Corrector residual history on the unit circle and its quadratic ratios."""
    result = predictor_corrector_step(
        circle_constraint,
        circle_jacobian,
        np.array([1.0, 0.0]),
        np.array([0.0, 1.0]),
        0.3,
        tol=CORRECTOR_TOL,
        max_iter=CORRECTOR_MAX_ITER,
    )
    hist = result.residual_history
    ratios = [
        b / a**2 for a, b in zip(hist[:-1], hist[1:], strict=True) if a > QUADRATIC_RATIO_FLOOR
    ]
    return {"iterations": result.iterations, "residual_history": list(hist), "ratios": ratios}


def _counterexample_entry() -> dict[str, Any]:
    """Minimum-norm limit versus the exact nearest point on the fold."""
    off = np.array(COUNTEREXAMPLE_POINT)
    limit, nearest = min_norm_correction_limit(off), nearest_point_on_fold(off)
    return {
        "start": off.tolist(),
        "gauss_newton_point": limit.tolist(),
        "gauss_newton_distance": float(np.linalg.norm(off - limit)),
        "nearest_point": nearest.tolist(),
        "nearest_distance": float(np.linalg.norm(off - nearest)),
    }


def _rank_drop_entry() -> dict[str, Any]:
    """Report the rank drop of ``u_1 u_2`` at the origin."""
    origin, jac0 = np.zeros(2), rank_drop_jacobian(np.zeros(2))
    try:
        predictor_corrector_step(
            rank_drop_constraint,
            rank_drop_jacobian,
            origin,
            np.array([1.0, 0.0]),
            0.1,
            tol=CORRECTOR_TOL,
            max_iter=CORRECTOR_MAX_ITER,
        )
        message, detected = "", False
    except RankChangeError as error:
        message, detected = str(error), True
    return {
        "expected_rank": 1,
        "jacobian_rank_at_origin": jacobian_rank(jac0, rtol=RANK_RTOL),
        "tangent_dimension_at_origin": int(local_tangent_basis(jac0, rtol=RANK_RTOL).shape[1]),
        "detected": detected,
        "message": message,
    }


def build_continuation_section() -> dict[str, Any]:
    """JSON-ready numbers for the P6 nonlinear-continuation section.

    Postconditions: only ``dict``/``list``/``float``/``int``/``bool``/``str`` values; no
    higher-than-quadratic order is asserted anywhere.
    """
    trace = trace_manifold(
        fold_constraint,
        fold_jacobian,
        np.array([-1.0, 1.0]),
        np.array([1.0, -2.0]),
        FOLD_TRACE_H,
        n_steps=FOLD_TRACE_STEPS,
        tol=CORRECTOR_TOL,
        max_iter=CORRECTOR_MAX_ITER,
    )
    return {
        "tangent_residual": {
            "circle": _tangent_residual_entry(
                circle_constraint, circle_jacobian, np.array([1.0, 0.0]), np.array([0.0, 1.0])
            ),
            "fold": _tangent_residual_entry(
                fold_constraint, fold_jacobian, np.array([1.0, 1.0]), np.array([1.0, 2.0])
            ),
        },
        "corrector_convergence": _quadratic_entry(),
        "fold_trace": {
            "points": trace.tolist(),
            "min_u2": float(trace[:, 1].min()),
            "max_manifold_error": float(np.max(np.abs(trace[:, 1] - trace[:, 0] ** 2))),
        },
        "nearest_point_counterexample": _counterexample_entry(),
        "rank_drop": _rank_drop_entry(),
    }
