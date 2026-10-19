"""Tests for the nonlinear solution-manifold continuation examples (P6)."""

import math

import numpy as np
import pytest

from src.tools.null_space_continuation_examples import (
    RankChangeError,
    build_continuation_section,
    circle_constraint,
    circle_jacobian,
    fold_constraint,
    fold_jacobian,
    jacobian_rank,
    local_tangent_basis,
    min_norm_correction_limit,
    nearest_point_on_fold,
    predictor_corrector_step,
    rank_drop_constraint,
    rank_drop_jacobian,
    tangent_step_residual,
    trace_manifold,
)


def test_tangent_basis_is_orthonormal_null_space() -> None:
    jac = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 1.0]])
    basis = local_tangent_basis(jac, rtol=1e-12)
    assert basis.shape == (3, 1)
    assert np.allclose(jac @ basis, 0.0, atol=1e-12)
    assert np.allclose(basis.T @ basis, np.eye(1))


def test_tangent_basis_reports_enlarged_null_space_at_rank_drop() -> None:
    jac = rank_drop_jacobian(np.zeros(2))
    assert jacobian_rank(jac, rtol=1e-12) == 0
    assert local_tangent_basis(jac, rtol=1e-12).shape == (2, 2)


def test_tangent_basis_validates_inputs() -> None:
    with pytest.raises(TypeError):
        local_tangent_basis([[1.0, 0.0]], rtol=1e-12)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        local_tangent_basis(np.ones(3), rtol=1e-12)
    with pytest.raises(ValueError):
        local_tangent_basis(np.ones((1, 3)), rtol=-1.0)
    with pytest.raises(ValueError):
        local_tangent_basis(np.array([[1.0, np.nan]]), rtol=1e-12)


@pytest.mark.parametrize(
    ("residual", "jac", "point", "direction"),
    [
        (circle_constraint, circle_jacobian, [1.0, 0.0], [0.0, 1.0]),
        (fold_constraint, fold_jacobian, [1.0, 1.0], [1.0, 2.0]),
    ],
)
def test_tangent_step_residual_is_second_order(residual, jac, point, direction) -> None:  # type: ignore[no-untyped-def]
    steps = np.array([0.4, 0.2, 0.1, 0.05, 0.025, 0.0125])
    values = [
        tangent_step_residual(residual, jac, np.array(point), np.array(direction), float(h))
        for h in steps
    ]
    slope = np.polyfit(np.log(steps), np.log(values), 1)[0]
    assert slope == pytest.approx(2.0, abs=0.1)


def test_circle_corrector_converges_quadratically() -> None:
    start = np.array([1.0, 0.0])
    result = predictor_corrector_step(
        circle_constraint,
        circle_jacobian,
        start,
        np.array([0.0, 1.0]),
        0.3,
        tol=1e-14,
        max_iter=20,
    )
    history = result.residual_history
    assert abs(circle_constraint(result.point)[0]) <= 1e-14
    assert result.iterations == len(history) - 1
    assert result.iterations >= 3
    # Quadratic: r_{k+1} <= C r_k^2 with C bounded by the analytic constant.
    for before, after in zip(history[:-1], history[1:], strict=True):
        if before > 1e-6:
            assert after <= 2.0 * before**2


def test_fold_corrector_converges_quadratically() -> None:
    result = predictor_corrector_step(
        fold_constraint,
        fold_jacobian,
        np.array([1.0, 1.0]),
        np.array([1.0, 2.0]),
        0.4,
        tol=1e-14,
        max_iter=20,
    )
    history = result.residual_history
    assert history[-1] <= 1e-14
    for before, after in zip(history[:-1], history[1:], strict=True):
        if before > 1e-6:
            assert after <= 2.0 * before**2


def test_min_norm_correction_is_not_nearest_point_projection() -> None:
    off = np.array([0.0, 1.0])
    result = predictor_corrector_step(
        fold_constraint,
        fold_jacobian,
        off,
        np.array([1.0, 0.0]),
        0.0,
        tol=1e-14,
        max_iter=20,
    )
    limit = min_norm_correction_limit(off)
    nearest = nearest_point_on_fold(off)
    assert np.allclose(result.point, limit, atol=1e-12)
    assert np.allclose(limit, [0.0, 0.0], atol=1e-12)
    gn_distance = float(np.linalg.norm(off - limit))
    best_distance = float(np.linalg.norm(off - nearest))
    assert fold_constraint(nearest)[0] == pytest.approx(0.0, abs=1e-12)
    assert best_distance == pytest.approx(math.sqrt(0.75), abs=1e-12)
    assert gn_distance == pytest.approx(1.0)
    assert best_distance < gn_distance - 0.1


def test_fold_trace_passes_through_turning_point() -> None:
    points = trace_manifold(
        fold_constraint,
        fold_jacobian,
        np.array([-1.0, 1.0]),
        np.array([1.0, -2.0]),
        0.25,
        n_steps=14,
        tol=1e-13,
        max_iter=20,
    )
    assert points.shape == (15, 2)
    assert np.max(np.abs(points[:, 1] - points[:, 0] ** 2)) <= 1e-12
    # u_2 decreases then increases: a turning point of the u_2 coordinate.
    drops = np.diff(points[:, 1])
    assert drops[0] < 0 < drops[-1]
    assert points[0, 0] < 0 < points[-1, 0]
    assert np.all(np.diff(points[:, 0]) > 0)


def test_rank_drop_detected_at_origin() -> None:
    with pytest.raises(RankChangeError, match="rank"):
        predictor_corrector_step(
            rank_drop_constraint,
            rank_drop_jacobian,
            np.zeros(2),
            np.array([1.0, 0.0]),
            0.1,
            tol=1e-10,
            max_iter=10,
        )


def test_rank_drop_detected_when_corrector_lands_on_origin() -> None:
    # Predictor from (1, 0) along (-1, 0) by h=1 lands exactly on the singular point.
    with pytest.raises(RankChangeError):
        predictor_corrector_step(
            rank_drop_constraint,
            rank_drop_jacobian,
            np.array([1.0, 0.0]),
            np.array([-1.0, 0.0]),
            1.0,
            tol=1e-10,
            max_iter=10,
        )


def test_rank_change_error_is_value_error() -> None:
    assert issubclass(RankChangeError, ValueError)


def test_step_validates_inputs() -> None:
    kwargs = {"tol": 1e-10, "max_iter": 5}
    u = np.array([1.0, 0.0])
    d = np.array([0.0, 1.0])
    with pytest.raises(ValueError):
        predictor_corrector_step(circle_constraint, circle_jacobian, u, d, float("nan"), **kwargs)
    with pytest.raises(ValueError):
        predictor_corrector_step(circle_constraint, circle_jacobian, u, d, 0.1, tol=0.0, max_iter=5)
    with pytest.raises(ValueError):
        predictor_corrector_step(
            circle_constraint, circle_jacobian, u, d, 0.1, tol=1e-10, max_iter=0
        )
    with pytest.raises(ValueError):
        # direction normal to the manifold has no tangent component
        predictor_corrector_step(
            circle_constraint, circle_jacobian, u, np.array([1.0, 0.0]), 0.1, **kwargs
        )
    with pytest.raises(ValueError):
        predictor_corrector_step(circle_constraint, circle_jacobian, u, np.ones(3), 0.1, **kwargs)
    with pytest.raises(RuntimeError, match="converge"):
        predictor_corrector_step(
            circle_constraint, circle_jacobian, u, d, 0.5, tol=1e-300, max_iter=1
        )


def test_section_is_json_ready_and_makes_no_cubic_claim() -> None:
    import json

    section = build_continuation_section()
    text = json.dumps(section, sort_keys=True)
    assert "cubic" not in text.lower()
    assert section["tangent_residual"]["circle"]["fitted_slope"] == pytest.approx(2.0, abs=0.1)
    assert section["nearest_point_counterexample"]["gauss_newton_distance"] > (
        section["nearest_point_counterexample"]["nearest_distance"]
    )
    assert section["rank_drop"]["jacobian_rank_at_origin"] == 0
    assert section["rank_drop"]["detected"] is True
    assert json.loads(text) == section
