"""Planar multi-body mechanics fixtures for mathematical verification."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure
from numpy.typing import NDArray

from scripts import make_proximal_distal_companion_figures as figures


def _cross_2d(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
    """Compute the scalar z-component of the 2D cross product a x b."""
    return float(a[0] * b[1] - a[1] * b[0])


def test_absolute_vs_relative_coordinates_power_and_dynamics() -> None:
    """Validate power invariance, metric transformation, and acceleration equivalence."""
    a_mat = np.array([[1.0, 0.0], [1.0, 1.0]], dtype=np.float64)
    theta_dot = np.array([2.0, 5.0], dtype=np.float64)
    q_dot = np.linalg.solve(a_mat, theta_dot)
    np.testing.assert_allclose(q_dot, np.array([2.0, 3.0], dtype=np.float64))

    tau_actuators = np.array([3.0, 4.0], dtype=np.float64)
    q_q = tau_actuators.copy()
    q_theta = np.linalg.solve(a_mat.T, q_q)
    np.testing.assert_allclose(q_theta, np.array([-1.0, 4.0], dtype=np.float64))
    np.testing.assert_allclose(a_mat.T @ q_theta, q_q)

    power_theta = float(np.dot(q_theta, theta_dot))
    power_q = float(np.dot(q_q, q_dot))
    power_naive = float(np.dot(tau_actuators, theta_dot))
    np.testing.assert_allclose(power_theta, 18.0)
    np.testing.assert_allclose(power_q, 18.0)
    np.testing.assert_allclose(power_naive, 26.0)

    m_theta = np.array([[2.0, 0.3], [0.3, 1.0]], dtype=np.float64)
    assert np.all(np.linalg.eigvalsh(m_theta) > 0.0)
    m_q = a_mat.T @ m_theta @ a_mat
    assert np.all(np.linalg.eigvalsh(m_q) > 0.0)

    ke_theta = 0.5 * float(theta_dot.T @ m_theta @ theta_dot)
    ke_q = 0.5 * float(q_dot.T @ m_q @ q_dot)
    np.testing.assert_allclose(ke_theta, 19.5)
    np.testing.assert_allclose(ke_q, 19.5)

    h_theta = np.array([0.5, -0.2], dtype=np.float64)
    h_q = a_mat.T @ h_theta
    alpha_theta = np.linalg.solve(m_theta, q_theta - h_theta)
    alpha_q = np.linalg.solve(m_q, q_q - h_q)
    np.testing.assert_allclose(alpha_theta, a_mat @ alpha_q)


@pytest.mark.parametrize("omega_second", [0.0, 1.0])
def test_instantaneous_diagonal_mass_matrix_coupling_and_energy_rate(omega_second: float) -> None:
    """Validate that zero instantaneous off-diagonal mass terms do not decouple acceleration."""
    param_a, param_c, param_b = 2.0, 1.0, 1.0
    delta = np.pi / 2.0
    omega = np.array([2.0, omega_second], dtype=np.float64)

    m_mat = np.array(
        [[param_a, param_b * np.cos(delta)], [param_b * np.cos(delta), param_c]],
        dtype=np.float64,
    )
    np.testing.assert_allclose(m_mat, np.diag([2.0, 1.0]), atol=1e-12)
    assert np.all(np.linalg.eigvalsh(m_mat) > 0.0)

    h_vec = np.array(
        [param_b * np.sin(delta) * (omega[1] ** 2), -param_b * np.sin(delta) * (omega[0] ** 2)],
        dtype=np.float64,
    )
    np.testing.assert_allclose(h_vec, [omega_second**2, -4.0], atol=1e-12)

    alpha = np.linalg.solve(m_mat, -h_vec)
    np.testing.assert_allclose(alpha, [-(omega_second**2) / 2, 4.0], atol=1e-12)
    assert not np.isclose(alpha[1], 0.0)

    m_dot_12 = -param_b * np.sin(delta) * (omega[0] - omega[1])
    m_dot = np.array([[0.0, m_dot_12], [m_dot_12, 0.0]], dtype=np.float64)
    term_work = float(omega.T @ m_mat @ alpha)
    term_mdot = 0.5 * float(omega.T @ m_dot @ omega)
    total_energy_rate = term_work + term_mdot
    np.testing.assert_allclose(total_energy_rate, 0.0, atol=1e-12)
    if omega_second:
        np.testing.assert_allclose([term_work, term_mdot], [2.0, -2.0])


def test_accelerating_reference_point_angular_balance_and_power() -> None:
    """Validate moving-point angular balance and power balance for hand-club model."""
    mass, i_g = 2.0, 0.5
    r_g_h = np.array([1.0, 0.0], dtype=np.float64)
    a_h = np.array([0.0, 1.0], dtype=np.float64)
    omega, tau_h = 0.0, 0.0

    i_h = i_g + mass * float(np.dot(r_g_h, r_g_h))
    np.testing.assert_allclose(i_h, 2.5)

    cross_fictitious = _cross_2d(r_g_h, a_h)
    np.testing.assert_allclose(cross_fictitious, 1.0)

    alpha = -(mass * cross_fictitious) / i_h
    np.testing.assert_allclose(alpha, -0.8)

    alpha_cross_r = np.array([-alpha * r_g_h[1], alpha * r_g_h[0]], dtype=np.float64)
    a_g = a_h + alpha_cross_r
    np.testing.assert_allclose(a_g, np.array([0.0, 0.2], dtype=np.float64))

    f_h = mass * a_g
    np.testing.assert_allclose(f_h, np.array([0.0, 0.4], dtype=np.float64))

    moment_about_h = _cross_2d(np.zeros(2, dtype=np.float64), f_h)
    moment_about_g = _cross_2d(-r_g_h, f_h)
    np.testing.assert_allclose(moment_about_h, 0.0, atol=1e-12)
    np.testing.assert_allclose(moment_about_g, -0.4)
    np.testing.assert_allclose(moment_about_g, i_g * alpha)

    v_h = np.array([0.0, 3.0], dtype=np.float64)
    v_g = v_h.copy()
    point_force_power = float(np.dot(f_h, v_h)) + tau_h * omega
    kinetic_energy_rate = mass * float(np.dot(v_g, a_g)) + i_g * omega * alpha
    np.testing.assert_allclose(point_force_power, 1.2)
    np.testing.assert_allclose(kinetic_energy_rate, 1.2)


def test_singular_inertia_limit_reaction_force() -> None:
    """Validate non-uniform acceleration limit and persistent reaction force as epsilon -> 0."""
    epsilons = np.array([1.0, 0.1, 0.01], dtype=np.float64)
    radius, tau_applied = 1.0, 1.0

    mass = epsilons
    i_g = epsilons
    i_h = i_g + mass * (radius**2)
    np.testing.assert_allclose(i_h, 2.0 * epsilons)

    alpha_unbounded = tau_applied / i_h
    np.testing.assert_allclose(alpha_unbounded, 1.0 / (2.0 * epsilons))

    tangential_force = mass * (alpha_unbounded * radius)
    np.testing.assert_allclose(tangential_force, np.full_like(epsilons, 0.5))

    alpha_bounded = 2.0
    force_bounded = mass * (alpha_bounded * radius)
    np.testing.assert_allclose(force_bounded, 2.0 * epsilons)
    assert force_bounded[-1] < force_bounded[0]


def test_inelastic_wrist_locking_impulse_and_dissipation() -> None:
    """Validate projection, momentum balance, and energy loss in instantaneous wrist lock."""
    m_mat = np.diag([2.0, 1.0]).astype(np.float64)
    v_minus = np.array([1.0, 0.0], dtype=np.float64)
    j_mat = np.array([[-1.0, 1.0]], dtype=np.float64)

    m_inv_jt = np.linalg.solve(m_mat, j_mat.T)
    gram_matrix = j_mat @ m_inv_jt
    constraint_violation = j_mat @ v_minus

    impulse_lambda = -np.linalg.solve(gram_matrix, constraint_violation)
    v_plus = v_minus + (m_inv_jt @ impulse_lambda).squeeze()
    np.testing.assert_allclose(v_plus, np.array([2.0 / 3.0, 2.0 / 3.0], dtype=np.float64))
    np.testing.assert_allclose(j_mat @ v_plus, np.array([0.0]), atol=1e-12)

    delta_momentum = m_mat @ (v_plus - v_minus)
    generalized_impulse = (j_mat.T @ impulse_lambda).squeeze()
    np.testing.assert_allclose(delta_momentum, generalized_impulse)
    np.testing.assert_allclose(generalized_impulse, np.array([-2.0 / 3.0, 2.0 / 3.0]))

    ke_before = 0.5 * float(v_minus.T @ m_mat @ v_minus)
    ke_after = 0.5 * float(v_plus.T @ m_mat @ v_plus)
    ke_loss = ke_before - ke_after
    np.testing.assert_allclose(ke_before, 1.0)
    np.testing.assert_allclose(ke_after, 2.0 / 3.0)
    np.testing.assert_allclose(ke_loss, 1.0 / 3.0)


@pytest.mark.integration
def test_pendulum_figure_contains_all_endpoints_and_changes_relative_angle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Illustrative opening must change relative geometry without cropping links."""
    captured: list[Figure] = []

    def capture(figure: Figure, stem: str) -> tuple[Path, Path]:
        captured.append(figure)
        return Path(stem + ".svg"), Path(stem + ".pdf")

    monkeypatch.setattr(figures, "_save", capture)
    figures.make_carry_release()
    figure = captured[0]
    relative_angles = []
    try:
        for axis in figure.axes:
            angles = []
            for line in axis.lines:
                points = line.get_xydata()
                assert np.all(points[:, 0] > axis.get_xlim()[0])
                assert np.all(points[:, 0] < axis.get_xlim()[1])
                assert np.all(points[:, 1] > axis.get_ylim()[0])
                assert np.all(points[:, 1] < axis.get_ylim()[1])
                displacement = points[1] - points[0]
                angles.append(np.arctan2(displacement[1], displacement[0]))
            relative_angles.append(angles[1] - angles[0])
        assert np.ptp(relative_angles) > 0.5
    finally:
        plt.close(figure)


@pytest.mark.integration
def test_pendulum_provider_links_are_revision_bound() -> None:
    """Source provenance must identify the mechanics text actually reviewed."""
    source = Path(__file__).resolve().parents[1] / (
        "articles/proximal_distal_companion/chapters/ch07_one_pendulum_to_two.qmd"
    )
    links = re.findall(
        r"https://github\.com/D-sorganization/UpstreamDrift/[^)\s]+",
        source.read_text(encoding="utf8"),
    )
    assert len(links) == 2
    assert all("/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/" in link for link in links)
