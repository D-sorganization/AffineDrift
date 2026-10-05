"""Rigorous tests for Volume II Control Is Motion landing page and mathematical foundations."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTROL_PAGE = ROOT / "books" / "control-is-motion.qmd"


def test_orbital_attraction_does_not_imply_timed_tracking_convergence() -> None:
    """A trajectory attracting to a periodic orbit with persistent phase offset has non-zero timed error.

    Plant on annulus r > 0:
      rdot = -(r - 1)
      thetadot = 1
    Reference orbit has r*(t) = 1, theta*(t) = t.
    Nearby trajectory starting at r(0) = r0 > 0, theta(0) = phi (phi != 0 mod 2pi):
      r(t) = 1 + (r0 - 1)*exp(-t) -> 1 as t -> inf.
      dist(x(t), orbit) = |r(t) - 1| -> 0 (orbital attraction).
    However, the squared Euclidean timed tracking error ||x(t) - x*(t)||^2 converges to
      2 - 2*cos(phi) != 0.
    """
    phi = 0.5  # Non-zero phase offset
    r0 = 1.8
    times = np.linspace(0, 100, 500)
    r_t = 1.0 + (r0 - 1.0) * np.exp(-times)
    theta_t = times + phi

    # Distance to the unit circle orbit
    dist_to_orbit = np.abs(r_t - 1.0)
    assert dist_to_orbit[-1] < 1e-12

    # Timed error ||x(t) - x*(t)||^2
    x_t = np.column_stack([r_t * np.cos(theta_t), r_t * np.sin(theta_t)])
    x_star = np.column_stack([np.cos(times), np.sin(times)])
    timed_error_sq = np.sum((x_t - x_star) ** 2, axis=1)

    theoretical_limit = 2.0 - 2.0 * np.cos(phi)
    assert timed_error_sq[-1] == pytest.approx(theoretical_limit, rel=1e-5)
    assert timed_error_sq[-1] > 0.2  # Persistent timed tracking error


def test_moving_projection_chain_rule_requires_moving_frame_derivatives() -> None:
    """Differentiating a time-dependent projection z = P(t) delta_x produces Pdot + P A terms.

    Plant: xdot = u.
    Nominal: x*(t) = [cos(t), sin(t)]^T, u*(t) = [-sin(t), cos(t)]^T.
    Linearization: A(t) = 0, B(t) = I_2.
    Perturbation: delta_x(t) = [eps, 0]^T with delta_u = 0.
    Moving projection: P(t) = [cos(t), 0] (1 x 2).
    Then z(t) = P(t) delta_x(t) = eps * cos(t).
    The derivative is zdot = -eps * sin(t).
    Evaluating (Pdot(t) + P(t)A(t)) delta_x + P(t)B(t) delta_u gives [-sin(t), 0] [eps, 0]^T = -eps * sin(t).
    An arbitrary projection without Pdot or without resolving tangential coupling does not yield an
    autonomous reduced system in z alone.
    """
    eps = 0.1
    t = 1.2
    delta_x = np.array([eps, 0.0])
    delta_u = np.array([0.0, 0.0])

    P = np.array([np.cos(t), 0.0])
    P_dot = np.array([-np.sin(t), 0.0])
    A = np.zeros((2, 2))
    B = np.eye(2)

    z_dot = (P_dot + P @ A) @ delta_x + (P @ B) @ delta_u
    expected = -eps * np.sin(t)
    assert z_dot == pytest.approx(expected)


def test_shifted_input_offset_violates_passive_port_storage() -> None:
    """Shifting a constant input offset into zero-input drift destroys passivity of the shifted port.

    Plant: m vdot + b v = u, with b > 0.
    Original port (u, v) is strictly output-passive with storage V = 0.5 * m * v^2:
      Vdot = v (u - b v) = u v - b v^2 <= u v.
    Introduce non-zero bias u0 > 0 and shifted control w = u - u0:
      m vdot + (b v - u0) = w.
    At steady state v_ss = (u0 - eps) / b with constant input w = -eps (0 < eps < u0):
      vdot = 0.
    The supply rate for port (w, v) is:
      supply = w * v_ss = -eps * (u0 - eps) / b < 0.
    At a constant state, any differentiable state storage S(v) has Sdot = 0 <= supply < 0,
    which is impossible. Hence algebraic zero-input drift is not automatically physically passive.
    """
    b = 2.0
    u0 = 10.0
    eps = 1.0
    v_ss = (u0 - eps) / b
    w = -eps
    supply = w * v_ss
    assert supply == pytest.approx(-4.5)
    assert supply < 0.0


def test_tube_invariance_does_not_imply_asymptotic_attraction() -> None:
    """Positive invariance or reachability containment of a tube does not establish convergence to zero.

    Plant: xdot = 0.
    Tube: [-1, 1].
    Initial condition x(0) = 0.5 stays at 0.5 for all t >= 0.
    The tube is positively invariant, but x(t) does not converge to 0.
    """
    initial_x = 0.5
    # For xdot = 0, state remains initial_x for all time
    trajectory = np.full(100, initial_x)
    assert np.all(np.abs(trajectory) <= 1.0)  # Invariant within [-1, 1]
    assert np.all(trajectory == 0.5)  # Never attracts to 0


def test_control_is_motion_landing_page_rigor_contracts() -> None:
    """Verify landing page source books/control-is-motion.qmd adheres to rigor contracts."""
    assert CONTROL_PAGE.exists(), f"Missing {CONTROL_PAGE}"
    content = CONTROL_PAGE.read_text(encoding="utf-8")

    # 1. Orbital stability must not be defined as convergence to x*(t) for all t
    assert "convergence to $x^*(t)$ for all $t$" not in content
    assert "convergence to `x*(t)` for all time" not in content
    assert (
        "distance to the orbit" in content.lower()
        or "distance to the nominal orbit" in content.lower()
        or "dist(" in content
    )

    # 2. Transverse dynamics must state moving-frame terms and chart requirement
    assert (
        "\\dot{P}" in content
        or "\\dot{P}(t)" in content
        or "Pdot" in content
        or "moving-frame" in content.lower()
    )
    assert (
        "transverse chart" in content.lower()
        or "poincaré" in content.lower()
        or "chart" in content.lower()
    )

    # 3. Drift must not be called purely passive geometry without qualification
    assert "Drift $f(x)$ encodes the passive geometry of motion" not in content
    assert "storage function" in content.lower() or "passivity" in content.lower()

    # 4. Funnel synthesis must not claim unqualified convergence certificates
    assert "certify convergence" not in content.lower()
    assert "invariance" in content.lower() or "containment" in content.lower()

    # 5. Framing must acknowledge task-dependent trade-offs rather than universal preference
    assert (
        "task-dependent" in content.lower()
        or "trade-off" in content.lower()
        or "complementary" in content.lower()
    )

    # 6. Primary sources and citations
    assert "Hauser" in content
    assert "Shiriaev" in content
    assert "Manchester" in content

    # 7. Preserve provisional and scaffolding guardrails
    assert "provisional" in content.lower()
    assert "scaffolded" in content.lower()
