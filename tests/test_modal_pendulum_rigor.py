"""Independent mechanics checks for the modal and pendulum appendices."""

from pathlib import Path

import numpy as np
import pytest
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
LENGTH = 1.1
DENSITY = 0.1
HEAD_MASS = 0.2
PIVOT_INERTIA = 0.4
GRAVITY_M_S2 = 9.81
STIFFNESS = 2500.0
DAMPING = 0.8
A = DENSITY * LENGTH / 5 + HEAD_MASS
B = DENSITY * LENGTH**2 / 4 + HEAD_MASS * LENGTH
J0 = PIVOT_INERTIA + DENSITY * LENGTH**3 / 3 + HEAD_MASS * LENGTH**2
P = DENSITY * LENGTH**2 / 2 + HEAD_MASS * LENGTH
Q = DENSITY * LENGTH / 3 + HEAD_MASS


def mass(eta: float) -> np.ndarray:
    """Return the Hessian of the declared planar kinetic energy."""
    return np.array([[J0 + A * eta**2, B], [B, A]])


def potential(theta: float, eta: float) -> float:
    """Return gravity plus the declared elastic potential."""
    return GRAVITY_M_S2 * (P * (1 - np.cos(theta)) + Q * eta * np.sin(theta)) + (
        0.5 * STIFFNESS * eta**2
    )


def gradient(theta: float, eta: float) -> np.ndarray:
    """Return the full potential gradient, including modal gravity."""
    return np.array(
        [
            GRAVITY_M_S2 * (P * np.sin(theta) + Q * eta * np.cos(theta)),
            GRAVITY_M_S2 * Q * np.sin(theta) + STIFFNESS * eta,
        ]
    )


def acceleration(state: np.ndarray, torque: float) -> np.ndarray:
    """Solve the coupled force balance with velocity and damping terms."""
    theta, eta, angular_rate, modal_rate = state
    bias = np.array([2 * A * eta * angular_rate * modal_rate, -A * eta * angular_rate**2])
    load = bias + gradient(theta, eta) + [0, DAMPING * modal_rate]
    return np.linalg.solve(mass(eta), np.array([torque, 0]) - load)


def test_complete_mass_matches_distributed_placement_energy() -> None:
    theta, eta = 0.4, 0.03
    rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    nodes, weights = leggauss(8)
    assembled = np.diag([PIVOT_INERTIA, 0.0])
    for s, weight in zip((nodes + 1) * LENGTH / 2, weights * LENGTH / 2, strict=True):
        shape = (s / LENGTH) ** 2
        jacobian = rotation @ np.array([[s, shape], [shape * eta, 0]])
        assembled += DENSITY * weight * jacobian.T @ jacobian
    head_jacobian = rotation @ np.array([[LENGTH, 1], [eta, 0]])
    assembled += HEAD_MASS * head_jacobian.T @ head_jacobian
    np.testing.assert_allclose(assembled, mass(eta), atol=1e-14)
    assert np.linalg.eigvalsh(assembled).min() > 0


def test_gravity_and_elastic_loads_match_potential_derivatives() -> None:
    coordinates = np.array([-0.7, 0.02])
    eps = 1e-6
    derivative = np.array(
        [
            (potential(*(coordinates + eps * row)) - potential(*(coordinates - eps * row)))
            / (2 * eps)
            for row in np.eye(2)
        ]
    )
    np.testing.assert_allclose(gradient(*coordinates), derivative, atol=1e-8)
    assert gradient(-np.pi / 4, 0)[1] < -1.6


def test_velocity_terms_satisfy_the_mechanical_power_identity() -> None:
    state = np.array([-0.5, 0.02, 8.0, -0.3])
    theta, eta, angular_rate, modal_rate = state
    velocity = state[2:]
    torque = 1.3
    mass_rate = np.diag([2 * A * eta * modal_rate, 0])
    energy_rate = (
        velocity @ mass(eta) @ acceleration(state, torque)
        + 0.5 * velocity @ mass_rate @ velocity
        + gradient(theta, eta) @ velocity
    )
    assert energy_rate == pytest.approx(angular_rate * torque - DAMPING * modal_rate**2)


def test_integrated_energy_matches_applied_work_and_dissipation() -> None:
    initial = np.array([-0.4, 0.01, 1.0, 0.0, 0.0])
    torque = 0.3

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        return np.r_[
            state[2:4], acceleration(state[:4], torque), state[2] * torque - DAMPING * state[3] ** 2
        ]

    result = solve_ivp(rhs, (0, 0.15), initial, rtol=1e-10, atol=1e-12)
    assert result.success
    final = result.y[:, -1]
    before = 0.5 * initial[2:4] @ mass(initial[1]) @ initial[2:4] + potential(*initial[:2])
    after = 0.5 * final[2:4] @ mass(final[1]) @ final[2:4] + potential(*final[:2])
    assert after - before == pytest.approx(final[4], abs=1e-9)


def test_reproducible_input_and_total_accelerations_are_distinct() -> None:
    input_acceleration = np.linalg.solve(mass(0), [1, 0])
    total = acceleration(np.array([-np.pi / 4, 0, 0, 0]), 1)
    np.testing.assert_allclose(input_acceleration, [2.47358342, -2.78835249], atol=5e-9)
    np.testing.assert_allclose(total, [2.70894668, 4.34133291], atol=5e-9)
    assert input_acceleration[1] < 0 < total[1]
    assert -B / A == pytest.approx(-1.1272522522522523)


def test_modal_sign_change_preserves_physical_input_response() -> None:
    transform = np.diag([1, -1])
    original = np.linalg.solve(mass(0), [1, 0])
    transformed_mass = transform.T @ mass(0) @ transform
    transformed = np.linalg.solve(transformed_mass, [1, 0])
    np.testing.assert_allclose(transform @ transformed, original)
    assert transformed[1] > 0


def test_frequency_depends_on_the_declared_base_constraint() -> None:
    clamped = np.sqrt(STIFFNESS / A) / (2 * np.pi)
    eigenvalues = eigh(np.diag([0.0, STIFFNESS]), mass(0), eigvals_only=True)
    free = np.sqrt(eigenvalues[1]) / (2 * np.pi)
    assert eigenvalues[0] == pytest.approx(0, abs=1e-10)
    assert clamped == pytest.approx(16.88937772903872)
    assert free == pytest.approx(22.006704996259074)
    assert free > clamped


def test_loaded_beam_mass_and_stiffness_follow_the_energy_functionals() -> None:
    nodes, weights = leggauss(8)
    s = (nodes + 1) / 2
    weights = weights / 2
    shapes = np.array([s**2, s**3])
    curvature = np.array([np.full_like(s, 2), 6 * s])
    matrix = np.einsum("i,ai,bi->ab", weights * 0.1, shapes, shapes)
    matrix += 0.2 * np.ones((2, 2)) + 0.03 * np.outer([2, 3], [2, 3])
    stiffness = np.einsum("i,ai,bi->ab", weights * 5, curvature, curvature)
    rates = np.array([0.3, -0.1])
    direct = 0.05 * np.sum(weights * (rates @ shapes) ** 2)
    direct += 0.1 * rates.sum() ** 2 + 0.015 * (rates @ [2, 3]) ** 2
    assert 0.5 * rates @ matrix @ rates == pytest.approx(direct)
    np.testing.assert_allclose(stiffness, [[20, 30], [30, 60]])
    assert np.linalg.eigvalsh(matrix).min() > 0


def test_mass_normalization_does_not_diagonalize_arbitrary_damping() -> None:
    matrix = np.array([[2.0, 0.3], [0.3, 1.0]])
    stiffness = np.diag([3.0, 5.0])
    _, modes = eigh(stiffness, matrix)
    np.testing.assert_allclose(modes.T @ matrix @ modes, np.eye(2), atol=1e-14)
    damping = np.array([[1.0, 0.8], [0.8, 1.0]])
    assert abs((modes.T @ damping @ modes)[0, 1]) > 0.1


def test_dynamic_tip_signs_match_the_weak_energy_balance() -> None:
    """Compare strong-form loads with virtual work for a manufactured beam motion."""
    nodes, weights = leggauss(8)
    s = (nodes + 1) / 2
    weights = weights / 2
    density, tip_mass, tip_inertia, rigidity, omega = 0.1, 0.2, 0.03, 5.0, 3.0
    # At sin(omega*t)=1, use w=s² and test function psi=s³ on the unit beam.
    acceleration_field = -(omega**2) * s**2
    distributed_load = density * acceleration_field
    force = -tip_mass * omega**2
    moment = -2 * tip_inertia * omega**2 + 2 * rigidity
    inertia_work = np.sum(weights * density * acceleration_field * s**3)
    inertia_work += -tip_mass * omega**2 - tip_inertia * 2 * omega**2 * 3
    elastic_work = np.sum(weights * rigidity * 2 * 6 * s)
    applied_work = np.sum(weights * distributed_load * s**3) + force + moment * 3
    assert inertia_work + elastic_work == pytest.approx(applied_work)


def test_body_gravity_torque_is_negative_potential_directional_derivative() -> None:
    rotation = Rotation.from_rotvec([0.3, -0.2, 0.1]).as_matrix()
    center = np.array([0.1, 0.0, -1.1])
    direction = np.array([0.2, -0.4, 0.3])
    body_force = rotation.T @ np.array([0, 0, -HEAD_MASS * GRAVITY_M_S2])
    torque = np.cross(center, body_force)
    eps = 1e-6
    upper = rotation @ Rotation.from_rotvec(eps * direction).as_matrix()
    lower = rotation @ Rotation.from_rotvec(-eps * direction).as_matrix()
    derivative = HEAD_MASS * GRAVITY_M_S2 * ((upper @ center)[2] - (lower @ center)[2]) / (2 * eps)
    assert torque @ direction == pytest.approx(-derivative, abs=1e-9)


def test_point_mass_pendulum_does_not_have_invertible_spatial_pivot_inertia() -> None:
    center = np.array([0, 0, -LENGTH])
    inertia = HEAD_MASS * (center @ center * np.eye(3) - np.outer(center, center))
    assert np.linalg.matrix_rank(inertia) == 2
    np.testing.assert_allclose(inertia @ center, 0)


@pytest.mark.parametrize("name", ["theory-part4", "drifter-manifesto", "affine-nature-golf-swing"])
def test_appendix_editions_preserve_reproducibility_and_validation_limits(name: str) -> None:
    text = (ROOT / "articles" / f"{name}.qmd").read_text(encoding="utf-8")
    for required in [
        "A Fully Specified Flexible Pendulum",
        "4.341333",
        "loaded mass inner product",
        "coordinate sign is a convention",
        "numerical verification does not establish empirical validity",
    ]:
        assert required in text
    assert "typical for a steel iron shaft" not in text
    assert "A positive-$\\Gamma$ convention would predict" not in text
