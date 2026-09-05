"""Independent checks for counterfactual, input and output distinctions."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
GRAVITY_M_S2 = 9.81


def test_pendulum_resultant_input_and_energy_rates_are_distinct() -> None:
    angle, speed, torque, damping = np.pi / 6, 2.0, 3.0, 0.2
    bias = GRAVITY_M_S2 * np.sin(angle) + damping * speed
    acceleration = torque - bias
    assert bias == pytest.approx(5.305)
    assert acceleration == pytest.approx(-2.305)
    assert acceleration + bias == pytest.approx(torque)
    kinetic_rate = speed * acceleration
    potential_rate = GRAVITY_M_S2 * np.sin(angle) * speed
    assert kinetic_rate == pytest.approx(-4.61)
    assert potential_rate == pytest.approx(GRAVITY_M_S2)
    assert kinetic_rate + potential_rate == pytest.approx(5.2)
    assert torque * speed == pytest.approx(6.0)


def test_free_branch_difference_contains_changed_drift() -> None:
    input_value = 2.0

    def rates(_time: float, states: np.ndarray) -> np.ndarray:
        return np.array([-states[0] + input_value, -states[1]])

    result = solve_ivp(rates, (0, 1), [0.5, 0.5], rtol=1e-10, atol=1e-12)
    actual, baseline = result.y[:, -1]
    assert actual - baseline == pytest.approx(2 * (1 - np.exp(-1)))
    assert actual - baseline != pytest.approx(input_value)


def test_stitched_drift_integral_is_not_a_forward_solution() -> None:
    time = np.linspace(0, 1, 10001)
    actual = 1 - np.exp(-time)
    stitched_integral = np.trapezoid(-actual, time)
    assert stitched_integral == pytest.approx(-np.exp(-1), abs=1e-8)
    assert stitched_integral != pytest.approx(0.0)


def test_nonlinear_scalar_flow_can_contract() -> None:
    def rates(_time: float, states: np.ndarray) -> np.ndarray:
        return -states - states**3

    time = np.linspace(0, 2, 101)
    result = solve_ivp(rates, (0, 2), [1, 1.1], t_eval=time, rtol=1e-10, atol=1e-12)
    error = np.abs(result.y[1] - result.y[0])
    assert np.all(error <= 0.1 * np.exp(-time) + 1e-10)


def test_double_integrator_position_error_grows_linearly() -> None:
    matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    initial = np.array([0.0, 0.02])
    for time in (0.1, 0.5, 1.0):
        assert (expm(matrix * time) @ initial)[0] == pytest.approx(0.02 * time)


def test_stable_eigenvalues_allow_transient_amplification() -> None:
    matrix = np.array([[-1.0, 10.0], [0.0, -1.0]])
    response = expm(matrix) @ np.array([0.0, 1.0])
    assert np.all(np.linalg.eigvals(matrix) < 0)
    assert np.linalg.norm(response) == pytest.approx(np.sqrt(101) / np.e)
    assert np.linalg.norm(response) > 3
    log_norm = np.linalg.eigvalsh((matrix + matrix.T) / 2)[-1]
    assert log_norm == pytest.approx(4.0)
    assert np.linalg.norm(response) < np.exp(log_norm)


def test_unit_scaling_changes_log_norm_but_preserves_output_sensitivity() -> None:
    matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    scale = np.diag([1000.0, 1.0])
    transformed = scale @ matrix @ np.linalg.inv(scale)
    assert np.linalg.eigvalsh((matrix + matrix.T) / 2)[-1] == pytest.approx(0.5)
    assert np.linalg.eigvalsh((transformed + transformed.T) / 2)[-1] == pytest.approx(500)
    output = np.array([[1.0, 0.0]])
    covariance = np.diag([1e-6, 4e-4])
    transport = expm(0.2 * matrix)
    original = output @ transport @ covariance @ transport.T @ output.T
    scaled_output = output @ np.linalg.inv(scale)
    scaled_transport = expm(0.2 * transformed)
    scaled_covariance = scale @ covariance @ scale.T
    revised = (
        scaled_output @ scaled_transport @ scaled_covariance @ scaled_transport.T @ scaled_output.T
    )
    np.testing.assert_allclose(original, revised)


def test_initial_error_and_model_bias_have_different_time_dependence() -> None:
    initial_error, bias = 0.02, 0.005

    def rate(_time: float, state: np.ndarray) -> np.ndarray:
        return -state + bias

    time = np.linspace(0, 2, 101)
    result = solve_ivp(rate, (0, 2), [initial_error], t_eval=time, rtol=1e-10, atol=1e-12)
    bound = initial_error * np.exp(-time) + bias * (1 - np.exp(-time))
    np.testing.assert_allclose(result.y[0], bound, atol=1e-10)
    assert bound[-1] < bound[0]


def test_stiffness_input_is_bilinear_and_control_affine() -> None:
    position, speed, mass, stiffness, damping = 0.3, -0.2, 2.0, 4.0, 0.1

    def acceleration(inputs: np.ndarray) -> float:
        torque, stiffness_change = inputs
        return float((torque - (stiffness + stiffness_change) * position - damping * speed) / mass)

    first, second = np.array([1.0, 2.0]), np.array([-2.0, 5.0])
    baseline = acceleration(np.zeros(2))
    assert acceleration(first + second) - baseline == pytest.approx(
        acceleration(first) + acceleration(second) - 2 * baseline
    )
    assert acceleration(first) - baseline == pytest.approx(
        np.array([1 / mass, -position / mass]) @ first
    )


def test_activation_is_retained_when_excitation_is_zero() -> None:
    decay_time = 0.05
    time = 0.02
    initial_activation = 0.4
    activation = initial_activation * np.exp(-time / decay_time)
    assert activation > 0.26
    assert activation != 0


def test_stiffness_schedule_has_an_energy_port_even_at_zero_drive() -> None:
    position, speed, stiffness, stiffness_rate, damping = 0.3, 0.2, 4.0, 2.0, 0.1
    acceleration = -stiffness * position - damping * speed
    kinetic_rate = speed * acceleration
    potential_rate = stiffness * position * speed + stiffness_rate * position**2 / 2
    expected = -damping * speed**2 + stiffness_rate * position**2 / 2
    assert kinetic_rate + potential_rate == pytest.approx(expected)
    assert expected == pytest.approx(0.086)


def test_feedback_shift_changes_zero_input_baseline() -> None:
    state, input_gain, bias_input, new_input = 0.3, 2.0, -0.4, 0.7
    drift = -state
    shifted_drift = drift + input_gain * bias_input
    assert shifted_drift != drift
    assert drift + input_gain * (bias_input + new_input) == pytest.approx(
        shifted_drift + input_gain * new_input
    )


def test_constraint_projection_preserves_acceleration_admissibility() -> None:
    mass = np.diag([2.0, 1.0])
    inverse = np.linalg.inv(mass)
    jacobian = np.array([[1.0, 1.0]])
    applied = np.array([1.0, 0.0])
    projected = inverse - inverse @ jacobian.T @ np.linalg.solve(
        jacobian @ inverse @ jacobian.T, jacobian @ inverse
    )
    response = projected @ applied
    np.testing.assert_allclose(response, [1 / 3, -1 / 3])
    np.testing.assert_allclose(jacobian @ response, 0, atol=1e-15)
    assert float((jacobian @ inverse @ applied)[0]) != 0


def test_missing_load_can_leave_a_residual_outside_input_image() -> None:
    input_map = np.array([[1.0], [0.0]])
    residual = np.array([3.0, -2.0])
    inferred, *_ = np.linalg.lstsq(input_map, residual, rcond=None)
    unexplained = residual - input_map @ inferred
    np.testing.assert_allclose(unexplained, [0.0, -2.0])


def test_fixed_contact_plane_includes_event_time_sensitivity() -> None:
    distance, horizontal_speed, vertical_speed = 1.0, 2.0, 0.1
    derivative = -vertical_speed * distance / horizontal_speed**2
    step = 1e-5
    forward = vertical_speed * distance / (horizontal_speed + step)
    backward = vertical_speed * distance / (horizontal_speed - step)
    assert (forward - backward) / (2 * step) == pytest.approx(derivative)
    assert derivative == pytest.approx(-0.025)


@pytest.mark.parametrize("name", ["theory-part2", "drifter-manifesto", "affine-nature-golf-swing"])
def test_counterfactual_editions_define_branch_and_uncertainty_scope(name: str) -> None:
    source = (ROOT / "articles" / f"{name}.qmd").read_text(encoding="utf-8")
    for phrase in [
        "Output Tolerance Determines the Horizon",
        "5.305",
        "freely evolving counterfactual",
        "does not identify individual muscle forces",
    ]:
        assert phrase.lower() in source.lower()
    for phrase in [
        "will cause the counterfactual trajectory to diverge exponentially",
        "How heavy does the club feel right now?",
        "20–50 ms",
    ]:
        assert phrase not in source


@pytest.mark.parametrize("name", ["theory-part3", "drifter-manifesto", "affine-nature-golf-swing"])
def test_invariance_editions_distinguish_state_input_and_evidence(name: str) -> None:
    source = (ROOT / "articles" / f"{name}.qmd").read_text(encoding="utf-8")
    for phrase in [
        "A Stiffness Input Can Still Be Affine",
        "Changing the Input Zero Changes the Baseline",
        "rugby place kick",
    ]:
        assert phrase in source
    for phrase in [
        "Spoiler: No.",
        "50% of this speed came from momentum",
        "reading off the rows of",
    ]:
        assert phrase not in source


def test_koike_reference_matches_the_actual_paper() -> None:
    bibliography = (ROOT / "references" / "affine-drift.bib").read_text(encoding="utf-8")
    entry = bibliography.split("@article{koike2019dynamic,", 1)[1].split("\n}", 1)[0]
    assert (
        "Direct and indirect effects of joint torque inputs during an induced speed analysis of a swinging motion"
        in entry
    )
    assert "Journal of Biomechanics" in entry
    assert "10.1016/j.jbiomech.2019.01.032" in entry
