"""Local UCM sample-variance decomposition in a declared Euclidean chart.

Callers supply synchronized repeated observations and the task Jacobian at their
mean configuration. Coordinates must be unwrapped and scaled consistently; the
function neither infers a neural mechanism nor corrects nonlinear task errors.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class UCMVariance:
    """Per-dimension sample variances; None marks an undefined group or ratio."""

    rank: int
    null_dimension: int
    variance_null: float | None
    variance_task: float | None
    ratio: float | None


def _real_matrix(values: ArrayLike, name: str) -> NDArray[np.float64]:
    """Reject non-matrix, complex and nonfinite inputs before decomposition."""
    if np.iscomplexobj(values):
        raise ValueError(f"{name} must contain real values")
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be a finite two-dimensional array")
    return matrix


def _sample_variance(deviations: NDArray[np.float64], basis: NDArray[np.float64]) -> float | None:
    """Divide projected squared deviations by sample and subspace dimensions."""
    dimension = basis.shape[1]
    if dimension == 0:
        return None
    with np.errstate(over="raise", invalid="raise"):
        try:
            projected = deviations @ basis
            variance = np.sum(projected**2) / ((len(deviations) - 1) * dimension)
        except FloatingPointError as exc:
            raise ValueError("sample variance overflow; rescale coordinates") from exc
    return float(variance)


def ucm_variance(
    samples: ArrayLike, jacobian: ArrayLike, *, relative_tolerance: float | None = None
) -> UCMVariance:
    """Decompose N-by-n data using an m-by-n task Jacobian at the sample mean.

    Use the unbiased sample denominator N-1 and normalize each projected trace
    by its numerical subspace dimension. Rank counts singular values greater
    than tolerance times the largest value; the default is max(m,n)*machine eps.
    None denotes a zero-dimensional variance or a ratio with zero denominator.
    Raises ValueError for invalid inputs or numerically unrepresentable variance.
    """
    data = _real_matrix(samples, "samples")
    task = _real_matrix(jacobian, "jacobian")
    if data.shape[0] < 2 or data.shape[1] < 1:
        raise ValueError("samples need at least two observations and one coordinate")
    if task.shape[0] < 1 or task.shape[1] != data.shape[1]:
        raise ValueError("jacobian needs at least one row and one column per coordinate")
    tolerance = (
        max(task.shape) * np.finfo(float).eps if relative_tolerance is None else relative_tolerance
    )
    if not np.isfinite(tolerance) or not 0 <= tolerance < 1:
        raise ValueError("relative_tolerance must be finite and in [0, 1)")
    _, singular_values, right_vectors = np.linalg.svd(task, full_matrices=True)
    if not np.all(np.isfinite(singular_values)):
        raise ValueError("singular values overflow; rescale the task Jacobian")
    rank = (
        int(np.count_nonzero(singular_values / singular_values[0] > tolerance))
        if singular_values[0] > 0
        else 0
    )
    with np.errstate(over="raise", invalid="raise"):
        try:
            deviations = data - data.mean(axis=0)
        except FloatingPointError as exc:
            raise ValueError("centering overflow; rescale coordinates") from exc
    variance_null = _sample_variance(deviations, right_vectors[rank:].T)
    variance_task = _sample_variance(deviations, right_vectors[:rank].T)
    ratio = None
    if variance_null is not None and variance_task is not None and variance_task > 0:
        ratio = variance_null / variance_task
        if not np.isfinite(ratio):
            raise ValueError("variance ratio exceeds floating-point range")
    return UCMVariance(rank, data.shape[1] - rank, variance_null, variance_task, ratio)
