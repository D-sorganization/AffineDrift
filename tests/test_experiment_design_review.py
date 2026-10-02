"""Test suite illustrating biomechanical, signal, covariance, and causal properties."""

import re
from itertools import product
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest


@pytest.mark.parametrize("d", [0.0, 0.2])
def test_bilateral_contact_and_force_couples(d: float) -> None:
    """Demonstrate force-couple and intrinsic contact-couple moment summation."""
    f_l = np.array([0.0, 1.0, 0.0])
    f_r = np.array([0.0, -1.0, 0.0])
    r_l = np.array([-d / 2.0, 0.0, 0.0])
    r_r = np.array([d / 2.0, 0.0, 0.0])

    moment_force_l = np.cross(r_l, f_l)
    moment_force_r = np.cross(r_r, f_r)
    force_couple = moment_force_l + moment_force_r

    assert np.isclose(force_couple[2], -d)
    contact_couples_z = -0.3 + -0.2
    total_moment_z = force_couple[2] + contact_couples_z
    assert np.isclose(total_moment_z, -d - 0.5)


def test_periodic_sine_filtering_discrepancy() -> None:
    """Illustrate filter discrepancy on periodic sine; periodic toy excludes boundary effects."""
    n_pts = 128
    k = 8
    mass = 2.0
    n = np.arange(n_pts)
    theta = 2.0 * np.pi * k / n_pts
    accel = np.sin(theta * n)
    force = mass * accel

    filter_a = (0.25, 0.5, 0.25)
    filter_b = (0.1, 0.8, 0.1)

    def apply_filter(x: np.ndarray, taps: tuple[float, float, float]) -> np.ndarray:
        return taps[0] * np.roll(x, 1) + taps[1] * x + taps[2] * np.roll(x, -1)

    out_a_accel = apply_filter(accel, filter_a)
    out_b_force = apply_filter(force, filter_b)
    out_a_force = apply_filter(force, filter_a)

    cos_ref = np.cos(theta * n)
    assert np.isclose(np.dot(out_a_accel, cos_ref), 0.0)
    assert np.isclose(np.dot(out_b_force, cos_ref), 0.0)

    analytic_gain_a = 0.5 + 0.5 * np.cos(theta)
    analytic_gain_b = 0.8 + 0.2 * np.cos(theta)
    assert np.allclose(out_a_accel, analytic_gain_a * accel)
    assert np.allclose(out_b_force, analytic_gain_b * force)

    assert not np.allclose(out_b_force, mass * out_a_accel)
    assert np.allclose(out_a_force, mass * out_a_accel)


def test_balanced_random_intercept_grand_mean_variance() -> None:
    """Scope grand mean variance under clustered covariance, not within-person contrasts."""
    n_clusters = 12
    m_obs = 10
    var_between = 4.0
    var_within = 1.0

    block = var_between * np.ones((m_obs, m_obs)) + var_within * np.eye(m_obs)
    sigma = np.kron(np.eye(n_clusters), block)
    total_obs = n_clusters * m_obs

    grand_mean_var = float(np.sum(sigma) / (total_obs**2))
    expected_var = (var_between / n_clusters) + (var_within / total_obs)
    naive_var = (var_between + var_within) / total_obs

    assert np.isclose(grand_mean_var, expected_var)
    assert np.isclose(grand_mean_var / naive_var, 8.2)


def test_deterministic_full_factorial_confounding_in_mediation() -> None:
    """Demonstrate naive mediation bias without stochastic sampling under unmodeled U."""
    grid = np.array(list(product((-1.0, 1.0), repeat=3)))
    t_vec, u_vec, e_vec = grid[:, 0], grid[:, 1], grid[:, 2]
    m_vec = t_vec + u_vec + e_vec
    y_vec = u_vec

    assert np.isclose(np.dot(t_vec, u_vec), 0.0)
    ones = np.ones_like(t_vec)

    # M ~ 1 + T
    x1 = np.column_stack([ones, t_vec])
    assert np.linalg.matrix_rank(x1) == 2
    coef1 = np.linalg.lstsq(x1, m_vec, rcond=None)[0]
    a_path = coef1[1]
    assert np.isclose(a_path, 1.0)

    # Y ~ 1 + T + M
    x2 = np.column_stack([ones, t_vec, m_vec])
    assert np.linalg.matrix_rank(x2) == 3
    coef2 = np.linalg.lstsq(x2, y_vec, rcond=None)[0]
    t_direct, b_mediator = coef2[1], coef2[2]
    assert np.isclose(t_direct, -0.5)
    assert np.isclose(b_mediator, 0.5)
    assert np.isclose(a_path * b_mediator, 0.5)

    # Adjusted: Y ~ 1 + T + M + U
    x_adj = np.column_stack([ones, t_vec, m_vec, u_vec])
    assert np.linalg.matrix_rank(x_adj) == 4
    coef_adj = np.linalg.lstsq(x_adj, y_vec, rcond=None)[0]
    assert np.isclose(coef_adj[2], 0.0)


@pytest.mark.parametrize(
    ("estimate", "se", "outcome"),
    [
        (0.0, 0.2, "inside"),
        (0.0, 0.5, "inconclusive"),
        (1.0, 0.2, "positive"),
    ],
)
def test_equivalence_bounds_vs_null_testing(estimate: float, se: float, outcome: str) -> None:
    """Evaluate two one-sided test boundaries; non-significance is not equivalence."""
    critical_z = NormalDist().inv_cdf(0.95)
    margin = 0.5
    ci_lower = estimate - critical_z * se
    ci_upper = estimate + critical_z * se

    if outcome == "inside":
        assert ci_lower > -margin and ci_upper < margin
    elif outcome == "inconclusive":
        assert ci_lower < -margin and ci_upper > margin
    elif outcome == "positive":
        assert ci_lower > margin


@pytest.mark.integration
def test_ch26_upstream_drift_links_require_pinned_commit() -> None:
    """Extract and validate UpstreamDrift link commit pins in chapter 26."""
    target_path = Path(__file__).resolve().parents[1] / (
        "articles/proximal_distal_companion/chapters/ch26_experiment_can_say_no.qmd"
    )
    content = target_path.read_text(encoding="utf-8")
    pattern = r"https?://[^\s)\]\"']*(?:UpstreamDrift|upstream_drift)[^\s)\]\"']*"
    links = re.findall(pattern, content)

    assert len(links) >= 3
    required_blob = "/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/"
    assert all(required_blob in link for link in links)
