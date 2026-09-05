"""Verify contact, energy, geometry, and the scope of the concluding case study."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
GRAVITY_M_S2 = 9.81


def test_coupled_mechanical_energy_balance_retains_inputs_and_dissipation() -> None:
    configuration = np.array([0.4, -0.2])
    velocity = np.array([0.7, -0.3])
    torque, force = np.array([0.2, -0.1]), np.array([0.3, -0.4])
    jacobian = np.array([[0.4, 0.2], [-0.3, 0.5]])
    damping = np.diag([0.1, 0.2])
    difference = configuration[0] - configuration[1]
    mass = np.array([[2.0, np.cos(difference)], [np.cos(difference), 1.0]])
    inertial = np.sin(difference) * np.array([velocity[1] ** 2, -velocity[0] ** 2])
    gravity = GRAVITY_M_S2 * np.array([2 * np.sin(configuration[0]), np.sin(configuration[1])])
    acceleration = np.linalg.solve(
        mass, torque + jacobian.T @ force - inertial - gravity - damping @ velocity
    )
    kinetic_gradient = np.sin(difference) * np.prod(velocity) * np.array([-1.0, 1.0])
    energy_rate = (kinetic_gradient + gravity) @ velocity + (mass @ velocity) @ acceleration
    power = velocity @ torque + (jacobian @ velocity) @ force - velocity @ damping @ velocity
    assert energy_rate == pytest.approx(power)


def test_stationary_ideal_constraint_force_can_have_zero_power() -> None:
    jacobian, velocity, reaction = np.array([[0.0, 1.0]]), np.array([2.0, 0.0]), np.array([100.0])
    generalized_force = jacobian.T @ reaction
    assert np.linalg.norm(generalized_force) == 100
    assert velocity @ generalized_force == 0


def test_first_contact_matches_independent_event_integration() -> None:
    initial = np.array([0.0, 0.0, 2.0, 0.1])

    def dynamics(_time: float, state: np.ndarray) -> np.ndarray:
        return np.array([state[2], state[3], 0.0, 0.0])

    def contact(_time: float, state: np.ndarray) -> float:
        return state[0] - 1

    result = solve_ivp(dynamics, (0, 1), initial, events=contact, rtol=1e-11, atol=1e-13)
    assert result.success
    assert result.t_events[0] == pytest.approx([0.5])
    assert result.y_events[0][0, 1] == pytest.approx(0.05)


def test_contact_output_derivative_includes_the_arrival_time_change() -> None:
    initial = np.array([0.0, 0.0, 2.0, 0.1])

    def contact_height(state: np.ndarray) -> float:
        return float(state[1] + state[3] * (1 - state[0]) / state[2])

    step = 1e-6
    derivative = np.array(
        [
            (contact_height(initial + step * axis) - contact_height(initial - step * axis))
            / (2 * step)
            for axis in np.eye(4)
        ]
    )
    assert derivative == pytest.approx([-0.05, 1.0, -0.025, 0.5], rel=1e-8)
    changed = initial + np.array([0.0, 0.0, 0.02, 0.0])
    exact_change = contact_height(changed) - contact_height(initial)
    assert exact_change == pytest.approx(-0.0004950495049505)
    assert derivative[2] * 0.02 == pytest.approx(-0.0005)
    assert initial[1] + initial[3] * 0.5 == changed[1] + changed[3] * 0.5


def test_phase_boundary_derivative_uses_actual_phase_rate() -> None:
    phase, phase_rate, error_rate = 0.3, 0.7, -0.2
    error = np.sqrt((0.2 + 0.1 * phase) / (1 + phase))

    def boundary_value(value: float, progress: float) -> float:
        return (1 + progress) * value**2 - (0.2 + 0.1 * progress)

    step = 1e-6
    difference = (
        boundary_value(error + step * error_rate, phase + step * phase_rate)
        - boundary_value(error - step * error_rate, phase - step * phase_rate)
    ) / (2 * step)
    analytic = 2 * (1 + phase) * error * error_rate + (error**2 - 0.1) * phase_rate
    assert boundary_value(error, phase) == pytest.approx(0)
    assert difference == pytest.approx(analytic, rel=1e-8)


def test_ellipsoid_output_bound_matches_constrained_optimization_and_coordinate_change() -> None:
    metric = np.array([[2.0, 0.3], [0.3, 1.0]])
    output, radius = np.array([0.2, 1.0]), 0.7
    expected = np.sqrt(radius * output @ np.linalg.solve(metric, output))
    result = minimize(
        lambda error: -output @ error,
        np.zeros(2),
        method="SLSQP",
        constraints={"type": "ineq", "fun": lambda error: radius - error @ metric @ error},
        options={"ftol": 1e-12, "maxiter": 200},
    )
    assert result.success
    assert -result.fun == pytest.approx(expected, rel=1e-8)
    change = np.array([[100.0, 0.0], [0.0, 0.1]])
    inverse = np.linalg.inv(change)
    changed_metric, changed_output = inverse.T @ metric @ inverse, output @ inverse
    assert np.sqrt(
        radius * changed_output @ np.linalg.solve(changed_metric, changed_output)
    ) == pytest.approx(expected)


def test_lyapunov_stability_does_not_require_attraction() -> None:
    rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    initial = np.array([0.01, 0.0])
    for time in (0.3, 1.0, 100.0):
        assert np.linalg.norm(expm(rotation * time) @ initial) == pytest.approx(0.01)


def test_wrench_point_shift_preserves_power_with_the_matching_twist() -> None:
    angular, linear = np.array([0.2, -0.4, 0.7]), np.array([1.0, 0.3, -0.2])
    torque, force = np.array([0.5, -0.1, 0.2]), np.array([2.0, -1.0, 3.0])
    shift = np.array([0.3, 0.4, -0.2])
    new_linear = linear + np.cross(angular, shift)
    new_torque = torque - np.cross(shift, force)
    assert torque @ angular + force @ linear == pytest.approx(
        new_torque @ angular + force @ new_linear
    )


def test_drift_authority_magnitude_ratio_does_not_prove_cancellation() -> None:
    drift, authority = np.array([1.0, 0.0]), np.array([[0.0], [1.0]])
    ratio = np.linalg.norm(drift) / 2
    best_command = np.linalg.lstsq(authority, -drift, rcond=None)[0]
    assert ratio < 1
    assert np.linalg.norm(drift + authority @ best_command) == 1


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch11_case_study_the_complete_golf_s.tex",
        "articles/motion-control/chapter11.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_case_editions_distinguish_protocol_calculation_and_evidence(source: str) -> None:
    text = (
        (ROOT / source)
        .read_text(encoding="utf-8")
        .split("Case Study: The Complete Golf Swing", 1)[1]
    )
    for required in [
        "does not report a solved",
        "first admissible contact",
        "0.000495",
        "actual phase rate",
        "not automatically an asymptotic region of attraction",
        "executable checks",
        "experimental validation",
    ]:
        assert required in text
    for incorrect in [
        "perfectly squaring",
        "mathematical secret of the professional",
        "passively swallowed",
        "chronological timing is irrelevant",
        "The SDP supplies",
        "physics irresistibly",
    ]:
        assert incorrect not in text


@pytest.mark.parametrize("volume", ["Volume_0", "Volume_I", "Volume_II"])
def test_shared_glossary_and_reading_preserve_technical_distinctions(volume: str) -> None:
    folder = ROOT / "articles/The_Geometry_of_Motion" / volume / "chapters"
    glossary = (folder / "glossary.tex").read_text(encoding="utf-8")
    for required in [
        "does not require return",
        "physical rotational freedom does not disappear",
        "one-parameter subgroup",
        "power is unchanged",
        "cotangent bundle",
        "generalized forces and any constraints",
        "directional alignment",
    ]:
        assert required in glossary
    reading = (folder / "further_reading.tex").read_text(encoding="utf-8")
    assert "edition, and errata" in reading
    assert "authors' companion site" in reading
    for unsupported in ["The definitive textbook", "are unmatched", "most intuitive treatment"]:
        assert unsupported not in reading
