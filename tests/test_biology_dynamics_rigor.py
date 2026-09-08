"""Independent identities and counterexamples for the biology chapter (#4294)."""

import numpy as np
import pytest
import sympy as sp
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar


def test_illustrative_force_velocity_law_has_correct_limits_and_matching_slopes() -> None:
    velocity = sp.symbols("velocity", real=True)
    shortening = (1 + velocity) / (1 - 4 * velocity)
    lengthening = 1 + sp.Rational(1, 2) * velocity / (sp.Rational(1, 10) + velocity)
    assert shortening.subs(velocity, -1) == 0
    assert shortening.subs(velocity, 0) == lengthening.subs(velocity, 0) == 1
    assert sp.diff(shortening, velocity).subs(velocity, 0) == 5
    assert sp.diff(lengthening, velocity).subs(velocity, 0) == 5
    assert sp.limit(lengthening, velocity, sp.oo) == sp.Rational(3, 2)
    assert shortening.subs(velocity, -sp.Rational(1, 2)) == sp.Rational(1, 6)
    assert lengthening.subs(velocity, sp.Rational(1, 10)) == sp.Rational(5, 4)
    for point in np.linspace(-1, 0, 21):
        assert float(sp.diff(shortening, velocity).subs(velocity, point)) > 0


def test_zero_excitation_retains_nonzero_activation() -> None:
    solution = solve_ivp(
        lambda _time, activation: -activation / 0.04,
        (0, 0.04),
        [0.8],
        rtol=1e-11,
        atol=1e-13,
    )
    assert solution.success
    assert solution.y[0, -1] == pytest.approx(0.8 / np.e, rel=1e-10)
    assert solution.y[0, -1] == pytest.approx(0.2943, abs=5e-5)


def test_tendon_force_integral_matches_stored_energy() -> None:
    extension = sp.symbols("extension", nonnegative=True)
    stored = sp.integrate(20000 * extension, (extension, 0, sp.Rational(1, 50)))
    assert stored == 4
    assert 20000 * sp.Rational(1, 50) == 400
    assert stored / sp.Rational(1, 50) == 200


def test_orbit_attraction_does_not_imply_phase_convergence() -> None:
    def dynamics(_time: float, state: np.ndarray) -> list[float]:
        return [1 - state[0], 2.0]

    solutions = [
        solve_ivp(dynamics, (0, 8), initial, rtol=1e-10, atol=1e-12)
        for initial in ([1.1, 0.0], [0.9, 0.2])
    ]
    assert all(solution.success for solution in solutions)
    first, second = [solution.y[:, -1] for solution in solutions]
    assert abs(first[0] - 1) < 4e-5
    assert abs(second[0] - 1) < 4e-5
    assert second[1] - first[1] == pytest.approx(0.2)
    points = [
        radius * np.array([np.cos(phase), np.sin(phase)]) for radius, phase in (first, second)
    ]
    assert np.linalg.norm(points[1] - points[0]) > 0.19


def test_hkb_potential_and_transition_direction() -> None:
    phase, first, second = sp.symbols("phase first second", real=True)
    potential = -first * sp.cos(phase) - second * sp.cos(2 * phase)
    drift = -sp.diff(potential, phase)
    derivative = sp.diff(drift, phase)
    assert derivative.subs(phase, 0) == -first - 4 * second
    assert derivative.subs(phase, sp.pi) == first - 4 * second
    assert (sp.diff(potential, phase) * drift + drift**2).simplify() == 0
    assert float(derivative.subs({phase: sp.pi, first: 1, second: 0.5})) == -1
    assert float(derivative.subs({phase: sp.pi, first: 1, second: 0.2})) == pytest.approx(0.2)


def test_ucm_tangent_step_has_second_order_task_error() -> None:
    nominal = np.array([1.0, 0.0])
    increment = np.array([0.0, 0.1])
    assert (2 * nominal) @ increment == 0
    assert np.sum((nominal + increment) ** 2) - nominal @ nominal == pytest.approx(0.01)


def test_dimension_normalized_isotropic_ucm_variances_are_equal() -> None:
    jacobian = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0]])
    row_projection = np.linalg.pinv(jacobian) @ jacobian
    null_projection = np.eye(3) - row_projection
    covariance = 0.04 * np.eye(3)
    assert np.trace(null_projection @ covariance) == pytest.approx(0.04)
    assert np.trace(row_projection @ covariance) / 2 == pytest.approx(0.04)
    np.testing.assert_allclose(jacobian @ null_projection, 0, atol=1e-14)


def test_double_integrator_has_full_control_and_observation_rank() -> None:
    system = np.array([[0.0, 1.0], [0.0, 0.0]])
    input_map = np.array([[0.0], [1.0]])
    output_map = np.array([[1.0, 0.0]])
    assert np.linalg.matrix_rank(input_map) == 1
    assert np.linalg.matrix_rank(np.hstack([input_map, system @ input_map])) == 2
    assert np.linalg.matrix_rank(np.vstack([output_map, output_map @ system])) == 2


def test_antagonist_pair_can_have_zero_torque_and_nonzero_stiffness() -> None:
    angle = sp.symbols("angle", real=True)
    arm = sp.Rational(3, 100)
    paths = [arm * angle, -arm * angle]
    forces = [100 + 10000 * length for length in paths]
    torque = -sum(
        force * sp.diff(length, angle) for force, length in zip(forces, paths, strict=True)
    )
    assert torque.subs(angle, 0) == 0
    assert -sp.diff(torque, angle) == 18


@pytest.mark.parametrize("force_sd,expected", [(10.0, 100.0), (40.0, 150.0)])
def test_bounded_stiffness_optimum_matches_independent_minimization(
    force_sd: float, expected: float
) -> None:
    def objective(stiffness: float) -> float:
        return force_sd**2 / stiffness**2 + 1e-6 * stiffness**2

    numerical = minimize_scalar(objective, bounds=(20, 150), method="bounded")
    assert numerical.success
    assert numerical.x == pytest.approx(expected, abs=2e-5)


@pytest.mark.parametrize("damping", [10.0, 20.0])
def test_compliance_peak_matches_analytic_gain(damping: float) -> None:
    mass, stiffness = 1.0, 100.0
    ratio = damping / (2 * np.sqrt(mass * stiffness))
    predicted = (
        1 / stiffness
        if ratio >= 1 / np.sqrt(2)
        else (1 / (2 * ratio * stiffness * np.sqrt(1 - ratio**2)))
    )
    frequency = np.linspace(0, 50, 100001)
    response = 1 / np.abs(stiffness - mass * frequency**2 + 1j * damping * frequency)
    assert response.max() == pytest.approx(predicted, rel=1e-8)


def test_separately_stable_parts_can_have_unstable_feedback_coupling() -> None:
    system = np.array([[-1.0, 2.0], [2.0, -1.0]])
    np.testing.assert_allclose(np.linalg.eigvalsh(system), [-3, 1])
    state = np.ones(2)
    assert state @ system @ state == 2
    decay = np.eye(3) - 0.2 * (np.eye(3, k=1) + np.eye(3, k=-1))
    assert np.linalg.eigvalsh(decay).min() == pytest.approx(1 - 0.2 * np.sqrt(2))
    assert np.linalg.eigvalsh(decay).min() > 0.7
