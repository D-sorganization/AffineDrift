"""Manufactured cart-pendulum explanatory test fixture and regression suite."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class CartPendulum:
    """System parameters for the manufactured cart-pendulum test fixture."""

    cart_mass: float = 2.0
    bob_mass: float = 1.0
    length: float = 1.0
    gravity: float = 9.81


def forward_dynamics(
    state: tuple[float, float, float, float],
    loads: tuple[float, float],
    params: CartPendulum,
) -> tuple[float, float]:
    """Compute forward accelerations (xdd, alpha) from generalized state and loads."""
    _, _, theta, omega = state
    f_load, tau = loads
    M, m, length, g = params.cart_mass, params.bob_mass, params.length, params.gravity
    c, s = np.cos(theta), np.sin(theta)
    mass_matrix = np.array([[M + m, m * length * c], [m * length * c, m * length**2]], dtype=float)
    bias = np.array([-m * length * s * omega**2, m * g * length * s], dtype=float)
    acc = np.linalg.solve(mass_matrix, np.array([f_load, tau], dtype=float) - bias)
    return float(acc[0]), float(acc[1])


def bob_kinematics(
    theta: float,
    omega: float,
    accels: tuple[float, float],
    length: float = 1.0,
) -> tuple[float, float]:
    """Compute planar cartesian acceleration components (ax, ay) of the point bob."""
    xdd, alpha = accels
    c, s = np.cos(theta), np.sin(theta)
    ax = xdd + length * c * alpha - length * s * omega**2
    ay = length * s * alpha + length * c * omega**2
    return float(ax), float(ay)


@pytest.mark.parametrize(
    "theta, omega, f_load, tau",
    [
        (np.pi / 6, 1.5, 4.0, -1.0),
        (-np.pi / 4, -2.0, -3.0, 2.5),
        (2 * np.pi / 3, 0.5, 0.0, 1.2),
        (np.pi / 2, -1.0, 5.0, 0.0),
    ],
)
def test_newton_momentum_balance(theta: float, omega: float, f_load: float, tau: float) -> None:
    """Verify independent Newton tangential and combined horizontal momentum balances."""
    p = CartPendulum()
    state = (0.0, 0.0, theta, omega)
    xdd, alpha = forward_dynamics(state, (f_load, tau), p)
    ax, ay = bob_kinematics(theta, omega, (xdd, alpha), p.length)

    horiz_momentum_rate = p.cart_mass * xdd + p.bob_mass * ax
    assert np.isclose(horiz_momentum_rate, f_load, rtol=1e-12, atol=1e-12)

    c, s = np.cos(theta), np.sin(theta)
    tangential_torque = p.bob_mass * p.length * (ax * c + (ay + p.gravity) * s)
    assert np.isclose(tangential_torque, tau, rtol=1e-12, atol=1e-12)


def test_explicit_acceleration_examples() -> None:
    """Verify explicit accelerations for baseline (3, 1) and intervention (0, 1)."""
    p = CartPendulum()
    state = (0.0, 0.0, 0.0, 0.0)

    xdd_31, alpha_31 = forward_dynamics(state, (3.0, 1.0), p)
    assert np.isclose(xdd_31, 1.0, atol=1e-12)
    assert np.isclose(alpha_31, 0.0, atol=1e-12)

    xdd_01, alpha_01 = forward_dynamics(state, (0.0, 1.0), p)
    assert np.isclose(xdd_01, -0.5, atol=1e-12)
    assert np.isclose(alpha_01, 1.5, atol=1e-12)


@pytest.mark.parametrize(
    "theta, omega, f_load, tau",
    [(0.0, 0.0, 3.0, 1.0), (np.pi / 3, 1.2, 5.0, 2.0)],
)
def test_immediate_intervention_vs_prescribed_replay(
    theta: float, omega: float, f_load: float, tau: float
) -> None:
    """Verify immediate force removal versus acceleration replay constraint."""
    p = CartPendulum()
    state = (0.0, 0.0, theta, omega)
    xdd_b, a_b = forward_dynamics(state, (f_load, tau), p)

    c, s = np.cos(theta), np.sin(theta)
    ml2 = p.bob_mass * p.length**2
    a_replay = (
        tau - p.bob_mass * p.gravity * p.length * s - p.bob_mass * p.length * c * xdd_b
    ) / ml2
    assert np.isclose(a_replay, a_b, rtol=1e-12, atol=1e-12)

    lam = (
        (p.cart_mass + p.bob_mass) * xdd_b
        + p.bob_mass * p.length * c * a_replay
        - p.bob_mass * p.length * s * omega**2
    )
    assert np.isclose(lam, f_load, rtol=1e-12, atol=1e-12)

    xdd_restored, a_restored = forward_dynamics(state, (lam, tau), p)
    assert np.allclose([xdd_restored, a_restored], [xdd_b, a_b], rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize(
    "case",
    [
        (np.pi / 4, 2.0, -1.5, 3.0, 1.5, 0.5),
        (-np.pi / 3, -1.2, 2.5, -4.0, 2.0, -1.0),
        (5 * np.pi / 6, 0.8, -0.7, 0.0, -3.0, 2.0),
    ],
)
def test_energy_derivative_power_balance(
    case: tuple[float, float, float, float, float, float],
) -> None:
    """Verify analytic dE/dt matches generalized power with and without constraint."""
    theta, xdot, omega, f_load, tau, xdd_target = case
    p = CartPendulum()
    state = (0.0, xdot, theta, omega)
    c, s = np.cos(theta), np.sin(theta)
    ml2 = p.bob_mass * p.length**2

    def compute_edot(ax_c: float, al_p: float) -> float:
        return float(
            (p.cart_mass + p.bob_mass) * xdot * ax_c
            + p.bob_mass * p.length * c * (ax_c * omega + xdot * al_p)
            - p.bob_mass * p.length * s * omega**2 * xdot
            + ml2 * omega * al_p
            + p.bob_mass * p.gravity * p.length * s * omega
        )

    xdd_free, alpha_free = forward_dynamics(state, (f_load, tau), p)
    edot_free = compute_edot(xdd_free, alpha_free)
    assert np.isclose(edot_free, f_load * xdot + tau * omega, rtol=1e-12, atol=1e-12)

    alpha_tgt = (
        tau - p.bob_mass * p.gravity * p.length * s - p.bob_mass * p.length * c * xdd_target
    ) / ml2
    lam = (
        (p.cart_mass + p.bob_mass) * xdd_target
        + p.bob_mass * p.length * c * alpha_tgt
        - p.bob_mass * p.length * s * omega**2
        - f_load
    )
    edot_constrained = compute_edot(xdd_target, alpha_tgt)
    power_constrained = f_load * xdot + tau * omega + lam * xdot
    assert np.isclose(edot_constrained, power_constrained, rtol=1e-12, atol=1e-12)


def test_dense_output_replay_distal_agreement() -> None:
    """Approximate distal replay trajectory agreement within declared tolerance."""
    p = CartPendulum()
    t_span = (0.0, 0.5)
    y0 = np.array([0.0, 0.5, np.pi / 6, 0.2], dtype=float)
    loads = (2.0, -0.5)
    ml2 = p.bob_mass * p.length**2

    def full_ode(t: float, y: NDArray[np.float64]) -> list[float]:
        st = (float(y[0]), float(y[1]), float(y[2]), float(y[3]))
        xdd, alpha = forward_dynamics(st, loads, p)
        return [float(y[1]), xdd, float(y[3]), alpha]

    sol_base = solve_ivp(full_ode, t_span, y0, dense_output=True, rtol=1e-10, atol=1e-10)
    assert sol_base.success

    def replay_ode(t: float, z: NDArray[np.float64]) -> list[float]:
        theta_r, omega_r = float(z[0]), float(z[1])
        st = sol_base.sol(t)
        xdd_b, _ = forward_dynamics(
            (float(st[0]), float(st[1]), float(st[2]), float(st[3])), loads, p
        )
        c, s = np.cos(theta_r), np.sin(theta_r)
        alpha_r = (
            loads[1] - p.bob_mass * p.gravity * p.length * s - p.bob_mass * p.length * c * xdd_b
        ) / ml2
        return [omega_r, float(alpha_r)]

    sol_replay = solve_ivp(replay_ode, t_span, y0[2:4], dense_output=True, rtol=1e-10, atol=1e-10)
    assert sol_replay.success

    # Approximate distal agreement within declared numerical tolerance (1e-7), not exact
    assert np.allclose(sol_replay.y[:, -1], sol_base.y[2:4, -1], rtol=1e-7, atol=1e-7)


@pytest.mark.parametrize(
    "theta, omega, f_load, tau",
    [
        (np.pi / 6, 1.2, 10.0, 2.0),
        (-np.pi / 4, -0.8, -6.0, 1.5),
        (2 * np.pi / 3, 2.0, 4.0, -3.0),
    ],
)
def test_coordinate_change_preserves_physical_coupling(
    theta: float, omega: float, f_load: float, tau: float
) -> None:
    """Verify coordinate change diagonalizes inertia and retains angular force coupling."""
    p = CartPendulum()
    a = p.bob_mass * p.length / (p.cart_mass + p.bob_mass)
    c = np.cos(theta)
    j_mat = np.array([[1.0, -a * c], [0.0, 1.0]], dtype=float)
    m_old = np.array(
        [
            [p.cart_mass + p.bob_mass, p.bob_mass * p.length * c],
            [p.bob_mass * p.length * c, p.bob_mass * p.length**2],
        ],
        dtype=float,
    )
    m_new = j_mat.T @ m_old @ j_mat
    assert np.isclose(m_new[0, 1], 0.0, atol=1e-12) and np.isclose(m_new[1, 0], 0.0, atol=1e-12)

    loads_new = j_mat.T @ np.array([f_load, tau], dtype=float)
    assert np.isclose(loads_new[1] - tau, -a * f_load * c, atol=1e-12)
    expected_inertia = p.bob_mass * p.length**2 - p.bob_mass**2 * p.length**2 * c**2 / (
        p.cart_mass + p.bob_mass
    )
    assert np.allclose(np.diag(m_new), [p.cart_mass + p.bob_mass, expected_inertia])
    new_velocity = np.array([0.4, omega])
    old_velocity = j_mat @ new_velocity
    assert np.isclose(old_velocity @ m_old @ old_velocity, new_velocity @ m_new @ new_velocity)
    assert np.isclose(np.array([f_load, tau]) @ old_velocity, loads_new @ new_velocity)


@pytest.mark.parametrize(
    "retired_claim",
    [
        "it is mostly kinematic forcing",
        "Timestep refinement distinguishes physical residual from numerical error.",
    ],
)
def test_chapter17_source_regression_guard(retired_claim: str) -> None:
    """Prevent retired inferences; this does not certify whole-source correctness."""
    root = Path(__file__).resolve().parents[1]
    path = root / "articles/proximal_distal_companion/chapters/ch17_moving_base.qmd"
    content = " ".join(path.read_text(encoding="utf-8").split())
    assert " ".join(retired_claim.split()) not in content


def test_figure_generator_source_regression_guard() -> None:
    """A prescribed base can move; its reaction cannot change its assigned path."""
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts/make_proximal_distal_companion_expanded_figures.py"
    content = " ".join(path.read_text(encoding="utf-8").split())
    assert "Back-Reaction Is Hidden When the Driver Cannot Move" not in content
