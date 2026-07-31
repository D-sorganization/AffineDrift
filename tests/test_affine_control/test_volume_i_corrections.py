"""Regression tests for the Volume I sign corrections filed as issue #3513.

Each test pins a formula *as printed in the book* against an independent
computation, never against a restatement of the same algebra. That distinction
is the whole point: every one of these errors survived years of review precisely
because the surrounding prose restated the wrong formula consistently.

The systems here are Volume I chapter 7's double pendulum (point masses at the
rod ends) and chapter 3's two-link arm, which are *not* the chapter 11 pendulum
that :func:`double_pendulum_mass_matrix` implements -- that one puts the centre
of mass at mid-link. They are written out locally rather than reusing that
function, because the published matrices are what is under test.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.dynamics import christoffel_coriolis

GRAVITY_M_S2 = 9.81


# --------------------------------------------------------------------------
# Volume I chapter 7: double pendulum, m1 = m2 = 1, l1 = l2 = 1
# --------------------------------------------------------------------------


def ch07_mass_matrix(q: np.ndarray) -> np.ndarray:
    """M(q) as printed at eq:ch7:mass-matrix-numeric."""
    c = np.cos(q[0] - q[1])
    return np.array([[2.0, c], [c, 1.0]])


def ch07_coriolis_as_printed(q: np.ndarray, qd: np.ndarray) -> np.ndarray:
    """C(q,qd) as printed at eq:ch7:coriolis-matrix-numeric, after the fix.

    The off-diagonal signs are opposite. Before the fix both were negative.
    """
    s = np.sin(q[0] - q[1])
    return np.array([[0.0, s * qd[1]], [-s * qd[0], 0.0]])


def ch07_potential(q: np.ndarray) -> float:
    return -GRAVITY_M_S2 * np.cos(q[0]) - GRAVITY_M_S2 * (np.cos(q[0]) + np.cos(q[1]))


def ch07_grad_potential(q: np.ndarray, h: float = 1e-6) -> np.ndarray:
    out = np.zeros(2)
    for k in range(2):
        fwd, bwd = q.copy(), q.copy()
        fwd[k] += h
        bwd[k] -= h
        out[k] = (ch07_potential(fwd) - ch07_potential(bwd)) / (2 * h)
    return out


STATES = [
    (np.array([0.7, -0.4]), np.array([1.3, -0.9])),
    (np.array([np.pi / 4, np.pi / 6]), np.array([2.0, -1.0])),
    (np.array([-1.2, 2.0]), np.array([-0.5, 3.1])),
    (np.array([0.0, 0.0]), np.array([1.0, 1.0])),
]


@pytest.mark.parametrize(("q", "qd"), STATES)
def test_ch07_printed_coriolis_matches_christoffel(q: np.ndarray, qd: np.ndarray) -> None:
    """The published matrix must equal the Christoffel symbols of the published M."""
    expected = christoffel_coriolis(ch07_mass_matrix, q, qd)
    np.testing.assert_allclose(ch07_coriolis_as_printed(q, qd), expected, atol=1e-7)


@pytest.mark.parametrize(("q", "qd"), STATES)
def test_ch07_skew_symmetry_of_mdot_minus_2c(q: np.ndarray, qd: np.ndarray) -> None:
    """Mdot - 2C must be skew-symmetric. A sign slip in C destroys this."""
    h = 1e-6
    mdot = np.zeros((2, 2))
    for k in range(2):
        fwd, bwd = q.copy(), q.copy()
        fwd[k] += h
        bwd[k] -= h
        mdot += (ch07_mass_matrix(fwd) - ch07_mass_matrix(bwd)) / (2 * h) * qd[k]
    residual = mdot - 2.0 * ch07_coriolis_as_printed(q, qd)
    np.testing.assert_allclose(residual, -residual.T, atol=1e-7)


def test_ch07_unforced_dynamics_conserve_energy() -> None:
    """The decisive check: with the wrong C_12 sign, energy drifts by ~14%.

    Integrating M qddot + C qd + dV/dq = 0 with the published matrices must hold
    total energy fixed to integrator accuracy.
    """
    q = np.array([0.7, -0.4])
    qd = np.array([1.3, -0.9])

    def energy(qq: np.ndarray, qqd: np.ndarray) -> float:
        return float(0.5 * qqd @ ch07_mass_matrix(qq) @ qqd + ch07_potential(qq))

    def deriv(state: np.ndarray) -> np.ndarray:
        pos, vel = state[:2], state[2:]
        rhs = -ch07_coriolis_as_printed(pos, vel) @ vel - ch07_grad_potential(pos)
        return np.concatenate([vel, np.linalg.solve(ch07_mass_matrix(pos), rhs)])

    state = np.concatenate([q, qd])
    e0 = energy(q, qd)
    dt = 1.0 / 20_000
    for _ in range(20_000):
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * dt * k1)
        k3 = deriv(state + 0.5 * dt * k2)
        k4 = deriv(state + dt * k3)
        state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    assert abs(energy(state[:2], state[2:]) - e0) < 1e-6 * abs(e0)


# --------------------------------------------------------------------------
# Volume I chapter 3: two-link arm
# --------------------------------------------------------------------------

ARM = {"I1": 0.13, "I2": 0.07, "m1": 2.3, "m2": 1.4, "l1": 0.9, "l2": 0.6}


def ch03_mass_matrix(q: np.ndarray) -> np.ndarray:
    """M(q) as printed in ch03."""
    p = ARM
    c2 = np.cos(q[1])
    m11 = (
        p["I1"]
        + p["m1"] * p["l1"] ** 2 / 4
        + p["m2"] * (p["l1"] ** 2 + p["l2"] ** 2 / 4)
        + p["m2"] * p["l1"] * p["l2"] * c2
        + p["I2"]
    )
    m12 = p["m2"] * (p["l2"] ** 2 / 4 + 0.5 * p["l1"] * p["l2"] * c2) + p["I2"]
    m22 = p["I2"] + p["m2"] * p["l2"] ** 2 / 4
    return np.array([[m11, m12], [m12, m22]])


def ch03_coriolis_vector_as_printed(q: np.ndarray, qd: np.ndarray) -> np.ndarray:
    """C(q,qd) qd as printed in ch03, after the fix.

    Before the fix the first row carried the opposite sign and both rows were a
    factor of two too large.
    """
    k = 0.5 * ARM["m2"] * ARM["l1"] * ARM["l2"] * np.sin(q[1])
    return np.array([-k * (2 * qd[0] * qd[1] + qd[1] ** 2), k * qd[0] ** 2])


@pytest.mark.parametrize(("q", "qd"), STATES)
def test_ch03_printed_coriolis_vector_matches_christoffel(q: np.ndarray, qd: np.ndarray) -> None:
    expected = christoffel_coriolis(ch03_mass_matrix, q, qd) @ qd
    np.testing.assert_allclose(ch03_coriolis_vector_as_printed(q, qd), expected, atol=1e-6)


@pytest.mark.parametrize(("q", "qd"), STATES)
def test_ch03_energy_identity_sign(q: np.ndarray, qd: np.ndarray) -> None:
    """eq:ch3:skew-symmetry: qd' C qd = +1/2 qd' Mdot qd, not -1/2.

    The minus sign as originally printed contradicted the energy balance two
    equations earlier, which is what made the passivity conclusion follow.
    """
    h = 1e-6
    mdot = np.zeros((2, 2))
    for k in range(2):
        fwd, bwd = q.copy(), q.copy()
        fwd[k] += h
        bwd[k] -= h
        mdot += (ch03_mass_matrix(fwd) - ch03_mass_matrix(bwd)) / (2 * h) * qd[k]
    lhs = qd @ christoffel_coriolis(ch03_mass_matrix, q, qd) @ qd
    assert lhs == pytest.approx(0.5 * qd @ mdot @ qd, abs=1e-6)


# --------------------------------------------------------------------------
# Volume I chapter 2: adjoint terminal condition
# --------------------------------------------------------------------------


def _rk4_step(x: float, dt: float, p: float) -> float:
    """One RK4 step of xdot = -p x + 1."""

    def rate(value: float) -> float:
        return -p * value + 1.0

    k1 = rate(x)
    k2 = rate(x + 0.5 * dt * k1)
    k3 = rate(x + 0.5 * dt * k2)
    k4 = rate(x + dt * k3)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def _cost(p: float, n: int = 2000, horizon: float = 1.0) -> float:
    """J = x(T)^2 + int_0^T x^2 dt for xdot = -p x + 1, x(0) = 1."""
    dt = horizon / n
    x = 1.0
    running = 0.0
    for _ in range(n):
        running += x * x * dt
        x = _rk4_step(x, dt, p)
    return x * x + running


def _adjoint_gradient(p: float, terminal_sign: float, n: int = 2000, horizon: float = 1.0) -> float:
    """dJ/dp via the chapter 2 adjoint, with lambda(T) = terminal_sign * dl/dx."""
    dt = horizon / n
    xs = np.empty(n + 1)
    xs[0] = 1.0
    for k in range(n):
        xs[k + 1] = _rk4_step(float(xs[k]), dt, p)

    lam = np.empty(n + 1)
    lam[n] = terminal_sign * 2.0 * xs[n]
    for k in range(n, 0, -1):
        lam[k - 1] = lam[k] - dt * (p * lam[k] - 2.0 * xs[k])
    return float(np.sum(lam[:-1] * (-xs[:-1])) * dt)


def test_ch02_adjoint_terminal_sign_is_positive() -> None:
    """lambda(T) = +dl/dx reproduces a finite-difference gradient; the minus does not."""
    p = 0.8
    reference = (_cost(p + 1e-6) - _cost(p - 1e-6)) / 2e-6
    assert _adjoint_gradient(p, +1.0) == pytest.approx(reference, rel=2e-3)
    # The published minus sign is not merely off by a sign -- it is a different
    # number, because the terminal condition feeds the whole backward sweep.
    assert _adjoint_gradient(p, -1.0) != pytest.approx(reference, rel=0.5)
    assert _adjoint_gradient(p, -1.0) != pytest.approx(-reference, rel=0.5)


# --------------------------------------------------------------------------
# Volume I chapter 4: hierarchical contraction
# --------------------------------------------------------------------------


@pytest.mark.parametrize("gain", [2.0, 3.0, 5.0, 20.0])
def test_ch04_cascade_is_not_contracting_in_the_unweighted_metric(gain: float) -> None:
    """The counterexample the theorem's warning box now states.

    Both subsystems contract at rate 1, yet the assembled system is not
    contracting in the identity metric once the coupling reaches 2.
    """
    jac = np.array([[-1.0, gain], [0.0, -1.0]])
    symmetric_part = 0.5 * (jac + jac.T)
    assert np.linalg.eigvalsh(symmetric_part).max() >= 0.0


@pytest.mark.parametrize("gain", [2.0, 3.0, 5.0, 20.0])
def test_ch04_weighted_metric_restores_contraction(gain: float) -> None:
    """...and the weight the corrected theorem introduces fixes it."""
    jac = np.array([[-1.0, gain], [0.0, -1.0]])
    theta = gain**2  # any theta > k^2 / (4 lambda1 lambda2) = gain^2 / 4
    metric = np.diag([1.0, theta])
    residual = jac.T @ metric + metric @ jac
    assert np.linalg.eigvalsh(0.5 * (residual + residual.T)).max() < 0.0


def test_ch04_pure_integrator_cascade_is_not_contracting() -> None:
    """The original worked example, qdot = v, had a zero Jacobian eigenvalue.

    It did not satisfy the theorem's own second hypothesis, so it could not have
    illustrated the theorem. The replacement adds position feedback.
    """
    without_feedback = np.array([[0.0, 1.0], [0.0, -5.0]])
    assert np.min(np.abs(np.linalg.eigvals(without_feedback))) == pytest.approx(0.0, abs=1e-12)

    alpha = 0.7
    with_feedback = np.array([[-alpha, 1.0], [0.0, -5.0]])
    assert np.max(np.linalg.eigvals(with_feedback).real) < 0.0


def test_ch04_van_der_pol_metric_does_not_certify_contraction() -> None:
    """The withdrawn metric violates its own condition at every sampled point."""
    epsilon, lam, beta, gamma = 0.5, 0.3, 1.2, 1.5

    def residual_max_eigenvalue(x1: float, x2: float) -> float:
        jac = np.array([[0.0, 1.0], [-1.0 - 2 * epsilon * x1 * x2, epsilon * (1 - x1**2)]])
        metric = np.diag([1.0, beta * (1 + gamma * x1**2)])
        metric_dot = np.diag([0.0, 2 * beta * gamma * x1 * x2])
        residual = jac.T @ metric + metric @ jac + metric_dot + 2 * lam * metric
        return float(np.linalg.eigvalsh(0.5 * (residual + residual.T)).max())

    grid = np.linspace(-3.0, 3.0, 25)
    worst = max(residual_max_eigenvalue(a, b) for a in grid for b in grid)
    assert worst > 0.0
    assert residual_max_eigenvalue(0.0, 0.0) > 1.0
