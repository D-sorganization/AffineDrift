"""Manufactured identifiability checks, not participant or provider validation."""

import importlib
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from scipy.optimize import minimize_scalar

from scripts import make_proximal_distal_companion_figures as base_figures


@pytest.mark.integration
def test_sensitivity_provider_links_are_revision_bound() -> None:
    """Provider claims retain the exact inspected source and data revision."""
    text = Path(
        "articles/proximal_distal_companion/chapters/ch21_sensitivity_identifiability.qmd"
    ).read_text(encoding="utf-8")
    links = re.findall(r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert len(links) == 2
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)


@pytest.mark.integration
def test_sensitivity_figure_keeps_nodes_and_labels_inside_axes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The full observation label and padded box must remain visible."""
    monkeypatch.setitem(sys.modules, "make_proximal_distal_companion_figures", base_figures)
    figures = importlib.import_module("scripts.make_proximal_distal_companion_expanded_figures")
    captured: list[Figure] = []
    monkeypatch.setattr(figures, "_save", lambda figure, _stem: captured.append(figure))
    figures.make_sensitivity()
    figure = captured[0]
    try:
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        for axis in figure.axes:
            nodes = [patch for patch in axis.patches if isinstance(patch, FancyBboxPatch)]
            for artist in [*nodes, *axis.texts]:
                bounds = artist.get_window_extent(renderer)
                assert axis.bbox.x0 < bounds.x0 < bounds.x1 < axis.bbox.x1
                assert axis.bbox.y0 < bounds.y0 < bounds.y1 < axis.bbox.y1
    finally:
        plt.close(figure)


def test_sum_difference_inverse_covariance_and_nullspace() -> None:
    """Verify parameter estimation, covariance, and nullspace for sum/difference model."""
    # Forward model: y1 = p1 + p2, y2 = p1 - p2 with y = [10, 2]
    a_mat = np.array([[1.0, 1.0], [1.0, -1.0]])
    y_obs = np.array([10.0, 2.0])
    # Diagonal noise variances: sigma1^2 = 1, sigma2^2 = 4
    noise_var = np.array([1.0, 4.0])
    weight_mat = np.diag(1.0 / noise_var)

    weighted_normal_matrix = a_mat.T @ weight_mat @ a_mat
    cov_p = np.linalg.inv(weighted_normal_matrix)
    expected_cov = np.array([[1.25, -0.75], [-0.75, 1.25]])
    np.testing.assert_allclose(cov_p, expected_cov, atol=1e-12)

    p_est = cov_p @ a_mat.T @ weight_mat @ y_obs
    np.testing.assert_allclose(p_est, np.array([6.0, 4.0]), atol=1e-12)

    # Sum-only design matrix has rank 1 and a non-trivial nullspace along [1, -1]^T
    a_sum_only = np.array([[1.0, 1.0]])
    _, s_vals, vh_mat = np.linalg.svd(a_sum_only)
    assert np.sum(s_vals > 1e-12) == 1
    null_vector = vh_mat[-1]
    np.testing.assert_allclose(a_sum_only @ null_vector, [0.0], atol=1e-12)


@pytest.mark.parametrize("p1", [-2.0, 6.0, 10.0])
def test_nuisance_profiling_and_slices(p1: float) -> None:
    """Verify optimal nuisance trajectory, profiled cost, and flat vs fixed slice profiles."""

    def cost_full(p2: float) -> float:
        return float((p1 + p2 - 10.0) ** 2 / 1.0 + (p1 - p2 - 2.0) ** 2 / 4.0)

    res = minimize_scalar(cost_full)
    assert res.success
    p2_opt = float(res.x)
    expected_p2 = 7.6 - 0.6 * p1
    assert p2_opt == pytest.approx(expected_p2, abs=1e-6)

    expected_cost = 0.8 * (p1 - 6.0) ** 2
    assert float(res.fun) == pytest.approx(expected_cost, abs=1e-6)

    # First-observation only: nuisance profiling over p2 yields flat zero-cost profile
    def cost_first_obs(p2: float) -> float:
        return float((p1 + p2 - 10.0) ** 2)

    res_first = minimize_scalar(cost_first_obs)
    assert res_first.success
    assert float(res_first.fun) == pytest.approx(0.0, abs=1e-6)

    # Fixed slice at p2 = 4 retains spurious curvature on first observation
    fixed_slice_cost = cost_first_obs(4.0)
    assert fixed_slice_cost == pytest.approx((p1 - 6.0) ** 2, abs=1e-6)


@pytest.mark.parametrize(
    ("matrix_factory", "expected_rank", "expected_cols"),
    [
        ("planar", 3, 4),
        ("separated_spatial", 5, 6),
        ("coincident_spatial", 3, 6),
        ("complete_spatial", 6, 12),
    ],
)
def test_wrench_map_ranks(matrix_factory: str, expected_rank: int, expected_cols: int) -> None:
    """Verify grasp matrix rank deficiencies under varied contact configurations."""
    if matrix_factory == "planar":
        # 2 planar contact points at (0, 0) and (1, 0); wrench = [fx, fy, tau_z]
        g_mat = np.array([[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]])
    elif matrix_factory == "separated_spatial":
        # 2 distinct 3D points at (0, 0, 0) and (1, 0, 0); zero torsional moment along baseline
        top = np.hstack([np.eye(3), np.eye(3)])
        skew_r2 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
        bottom = np.hstack([np.zeros((3, 3)), skew_r2])
        g_mat = np.vstack([top, bottom])
    elif matrix_factory == "coincident_spatial":
        # 2 coincident 3D points at origin
        g_mat = np.vstack([np.hstack([np.eye(3), np.eye(3)]), np.zeros((3, 6))])
    else:
        # 2 complete 6D spatial wrenches mapped directly to resultant wrench
        g_mat = np.hstack([np.eye(6), np.eye(6)])

    rank = int(np.linalg.matrix_rank(g_mat))
    assert g_mat.shape[1] == expected_cols
    assert rank == expected_rank


def test_symmetric_global_regression_vs_local_derivative() -> None:
    """Verify global polynomial regression slope divergence from local derivative at origin."""
    x_vals = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    design = np.column_stack((np.ones_like(x_vals), x_vals))
    assert np.isclose(np.mean(x_vals), 0.0)

    # Regression of x^2 on x: zero slope despite variation
    y_quad = x_vals**2
    slope_quad = float(np.linalg.lstsq(design, y_quad, rcond=None)[0][1])
    assert np.isclose(slope_quad, 0.0, atol=1e-12)
    assert np.var(y_quad) > 0.0

    # Regression of x^3 on x: global slope 3.4 vs local derivative 0.0 at origin
    y_cube = x_vals**3
    slope_cube = float(np.linalg.lstsq(design, y_cube, rcond=None)[0][1])
    assert slope_cube == pytest.approx(3.4, abs=1e-12)

    local_derivative_at_zero = 3.0 * (0.0**2)
    assert local_derivative_at_zero == 0.0
    assert slope_cube != local_derivative_at_zero


def test_cubic_injectivity_and_quadratic_sign_ambiguity() -> None:
    """Check illustrative values; finite sampling is not a global injectivity proof."""
    # Cubic derivative vanishes at zero but remains strictly injective on R
    assert 3.0 * (0.0**2) == 0.0
    sample_x = np.linspace(-3.0, 3.0, 31)
    cubed_vals = sample_x**3
    assert len(cubed_vals) == len(np.unique(cubed_vals))

    # Nonzero derivatives at two indistinguishable points do not prove global recovery.
    assert 2.0 * (-2.0) != 0.0 and 2.0 * 2.0 != 0.0
    assert (-2.0) ** 2 == (2.0) ** 2
    assert len(np.unique(sample_x**2)) < len(sample_x)
