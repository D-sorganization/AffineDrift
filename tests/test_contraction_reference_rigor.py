"""Counterexamples and source checks for the contraction reference."""

from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import eigvalsh, expm


def test_metric_derivative_requires_covariant_matrix_order() -> None:
    dynamics = np.array([[-1.0, 3.0], [0.0, -2.0]])
    metric = np.array([[0.5, 0.5], [0.5, 1.0]])
    correct = dynamics.T @ metric + metric @ dynamics
    reversed_order = dynamics @ metric + metric @ dynamics.T
    assert correct == pytest.approx(-np.eye(2))
    assert np.linalg.eigvalsh(reversed_order)[-1] > 2.0


def test_stable_step_eigenvalues_do_not_stabilize_a_time_varying_product() -> None:
    first = np.array([[0.5, 2.0], [0.0, 0.5]])
    second = first.T
    assert max(abs(np.linalg.eigvals(first))) == pytest.approx(0.5)
    assert max(abs(np.linalg.eigvals(second))) == pytest.approx(0.5)
    assert max(abs(np.linalg.eigvals(second @ first))) > 4.0


def test_riccati_metric_rate_is_not_the_spectral_decay_rate() -> None:
    dynamics = np.array([[0.0, 1.0], [0.0, 0.0]])
    inputs = np.array([[0.0], [1.0]])
    metric = np.array([[12.0, 4.0], [4.0, 3.0]])
    gain = np.array([[4.0, 3.0]])
    cost = np.diag([16.0, 1.0]) + gain.T @ gain
    closed = dynamics - inputs @ gain
    assert closed.T @ metric + metric @ closed == pytest.approx(-cost)
    assert min(eigvalsh(cost, metric)) / 2 == pytest.approx(1.27639320225)
    assert max(np.linalg.eigvals(closed).real) == pytest.approx(-1.5)


def test_finite_horizon_metric_can_shrink_while_state_error_grows() -> None:
    horizon, time = 1.0, 0.5

    def metric(t: float) -> float:
        return float((np.exp(2 * (horizon - t)) - 1) / 2)

    assert np.exp(time) > 1
    assert metric(time) * np.exp(2 * time) < metric(0)
    assert metric(horizon) == 0


def test_task_pullback_is_singular_and_is_not_two_link_inertia() -> None:
    jacobian = np.array([[0.0, 0.0], [2.0, 1.0]])
    pullback = jacobian.T @ jacobian
    physical_mass = np.array([[8 / 3, 5 / 6], [5 / 6, 1 / 3]])
    assert np.linalg.det(pullback) == pytest.approx(0)
    assert np.linalg.det(physical_mass) > 0
    assert not np.allclose(pullback, physical_mass)


def test_critical_damping_energy_is_not_a_strict_contraction_certificate() -> None:
    dynamics = np.array([[0.0, 1.0], [-1.0, -2.0]])
    error = np.array([1.0, 0.0])
    assert error @ (dynamics.T + dynamics) @ error == 0
    assert np.linalg.norm(expm(dynamics) @ error) > np.exp(-1)
    metric = np.array([[1.5, 0.5], [0.5, 0.5]])
    assert dynamics.T @ metric + metric @ dynamics == pytest.approx(-np.eye(2))


def test_closed_loop_noise_has_a_nonzero_stationary_error_floor() -> None:
    # dx = -x dt + sigma dW; independent copies have twice the covariance.
    sigma, time = 2.0, 5.0
    variance = sigma**2 * (1 - np.exp(-2 * time)) / 2
    assert variance == pytest.approx(2.0, rel=1e-4)
    assert 2 * variance > 3.99


def test_new_reference_replaces_unsupported_certificates_and_results() -> None:
    root = Path(__file__).resolve().parents[1]
    for suffix in ("qmd", "tex"):
        source = (
            root
            / "articles/tangent-hyperplane-articles/Advanced"
            / f"Contraction_Tangent_Unification.{suffix}"
        ).read_text(encoding="utf-8")
        assert "Saltation" in source
        assert "1.276" in source
        assert "sufficiently large" not in source
        assert "0.82" not in source
        assert "28.7" not in source
        assert "Max eigenvalue: -0.3218" not in source
        assert "geodesic spray" not in source
