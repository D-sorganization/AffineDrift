"""Independent covariance, geometry and input-contract checks for UCM analysis."""

import numpy as np
import pytest
from numpy.testing import assert_allclose


def test_manufactured_covariance_and_dimension_normalization() -> None:
    """Six symmetric observations have covariance diag(9, 1, 1)."""
    from src.affine_control.ucm_analysis import ucm_variance

    axes = np.diag(np.sqrt(2.5 * np.array([9.0, 1.0, 1.0])))
    samples = np.vstack((axes, -axes)) + [4.0, 2.0, -1.0]
    result = ucm_variance(samples, [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    assert result.rank == 2
    assert result.null_dimension == 1
    assert result.variance_null == pytest.approx(9.0)
    assert result.variance_task == pytest.approx(1.0)
    assert result.ratio == pytest.approx(9.0)
    assert result.variance_null + 2 * result.variance_task == pytest.approx(
        np.trace(np.cov(samples, rowvar=False, ddof=1))
    )


def test_orthogonal_coordinate_change_and_task_rescaling() -> None:
    """Orthogonal re-expression preserves the declared Euclidean metric."""
    from src.affine_control.ucm_analysis import ucm_variance

    samples = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 3.0], [0.0, -3.0]])
    rotation = np.array([[0.6, -0.8], [0.8, 0.6]])
    jacobian = np.array([[1.0, 0.0]])
    expected = ucm_variance(samples, jacobian)
    for scale in [1e-100, 1.0, 1e100]:
        actual = ucm_variance(samples @ rotation.T, scale * jacobian @ rotation.T)
        assert actual.rank == expected.rank
        assert actual.variance_null == pytest.approx(expected.variance_null)
        assert actual.variance_task == pytest.approx(expected.variance_task)
        assert actual.ratio == pytest.approx(expected.ratio)


@pytest.mark.parametrize("jacobian,rank", [([[1.0, 0.0], [2.0, 0.0]], 1), ([[0, 0]], 0)])
def test_rank_uses_independent_constraints(jacobian: list[list[float]], rank: int) -> None:
    """Repeated constraint rows do not consume extra task dimensions."""
    from src.affine_control.ucm_analysis import ucm_variance

    result = ucm_variance([[1.0, 2.0], [-1.0, -2.0]], jacobian)
    assert result.rank == rank
    assert result.null_dimension == 2 - rank
    if rank == 0:
        assert result.variance_task is None
        assert result.ratio is None


def test_full_rank_and_zero_variance_are_explicitly_undefined() -> None:
    """Absent groups and zero denominators are not invented zero or infinite evidence."""
    from src.affine_control.ucm_analysis import ucm_variance

    full = ucm_variance([[1.0, 2.0], [-1.0, -2.0]], np.eye(2))
    assert full.variance_null is None and full.ratio is None
    zero = ucm_variance(np.zeros((4, 2)), [[1.0, 0.0]])
    assert zero.variance_null == zero.variance_task == 0.0
    assert zero.ratio is None


def test_relative_rank_tolerance_is_explicit() -> None:
    """Near-singular task directions require a declared numerical rank policy."""
    from src.affine_control.ucm_analysis import ucm_variance

    data = [[1.0, 2.0], [-1.0, -2.0]]
    jacobian = np.diag([1.0, 1e-8])
    assert ucm_variance(data, jacobian, relative_tolerance=1e-6).rank == 1
    assert ucm_variance(data, jacobian, relative_tolerance=1e-10).rank == 2


@pytest.mark.parametrize(
    "samples,jacobian",
    [
        ([1, 2], [[1, 0]]),
        ([[1, 2]], [[1, 0]]),
        (np.empty((3, 0)), np.empty((1, 0))),
        ([[1, 2], [3, np.nan]], [[1, 0]]),
        ([[1, 2], [3, 4]], [[np.inf, 0]]),
        ([[1j, 2], [3, 4]], [[1, 0]]),
        ([[1, 2], [3, 4]], [[1j, 0]]),
        ([[1, 2], [3, 4]], [1, 0]),
        ([[1, 2], [3, 4]], [[1, 0, 0]]),
        ([[1, 2], [3, 4]], np.empty((0, 2))),
    ],
)
def test_invalid_arrays_are_rejected(samples: object, jacobian: object) -> None:
    """The analysis requires real finite repeated observations and a matching matrix."""
    from src.affine_control.ucm_analysis import ucm_variance

    with pytest.raises(ValueError):
        ucm_variance(samples, jacobian)


@pytest.mark.parametrize("tolerance", [-1.0, 1.0, np.inf, np.nan])
def test_invalid_tolerance_is_rejected(tolerance: float) -> None:
    """Relative singular-value thresholds must remain in the unit interval."""
    from src.affine_control.ucm_analysis import ucm_variance

    with pytest.raises(ValueError):
        ucm_variance([[1, 2], [3, 4]], [[1, 0]], relative_tolerance=tolerance)


def test_nonlinear_tangent_step_is_not_an_exact_task_solution() -> None:
    """The tangent line of a circle leaves the level set at second order."""
    point = np.array([1.0, 0.0])
    displacement = np.array([0.0, 0.1])
    assert (2 * point) @ displacement == 0.0
    assert np.dot(point + displacement, point + displacement) - 1 == pytest.approx(0.01)
    exact = np.array([np.sqrt(0.99), 0.1])
    assert exact @ exact == pytest.approx(1.0)


def test_identical_covariance_does_not_identify_feedback() -> None:
    """Two distinct stable OU models have the same stationary covariance."""
    covariance = np.diag([1.0, 9.0])
    models = [(-np.eye(2), 2 * covariance), (-np.diag([9.0, 1.0]), 18 * np.eye(2))]
    for drift, diffusion_covariance in models:
        assert np.all(np.linalg.eigvalsh(drift) < 0)
        assert_allclose(drift @ covariance + covariance @ drift.T + diffusion_covariance, 0)


def test_unrepresentable_singular_values_do_not_become_zero_rank() -> None:
    """Finite entries can overflow an SVD; reject them instead of inventing nullity."""
    from src.affine_control.ucm_analysis import ucm_variance

    with pytest.raises(ValueError, match="singular values"):
        ucm_variance([[1.0, 2.0], [-1.0, -2.0]], np.full((2, 2), 1e308))
