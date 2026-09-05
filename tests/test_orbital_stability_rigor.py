"""Independent counterexamples for orbital and finite-event stability claims."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]


def test_persistent_phase_offset_is_bounded_not_asymptotically_zero() -> None:
    offset = 0.1
    times = np.linspace(0, 20, 100)
    reference = np.column_stack([np.cos(times), np.sin(times)])
    shifted = np.column_stack([np.cos(times - offset), np.sin(times - offset)])
    np.testing.assert_allclose(np.linalg.norm(reference - shifted, axis=1), 2 * np.sin(offset / 2))


def test_nonlinear_radial_terms_decide_unit_multiplier_case() -> None:
    initial, time = 0.2, 2.0
    stable = initial / np.sqrt(1 + 2 * initial**2 * time)
    unstable = initial / np.sqrt(1 - 2 * initial**2 * time)
    assert stable < initial < unstable
    # Both radial vector fields have derivative zero at the nominal circle.
    assert np.exp(0 * 2 * np.pi) == 1


def test_oscillator_feedback_requires_phase_dependent_input_factor() -> None:
    gain = 0.7
    old_exponent = quad(lambda time: -gain * np.sin(time), 0, 2 * np.pi)[0]
    corrected_exponent = quad(lambda time: -gain * np.sin(time) ** 2, 0, 2 * np.pi)[0]
    assert np.exp(old_exponent) == pytest.approx(1.0)
    assert np.exp(corrected_exponent) == pytest.approx(np.exp(-gain * np.pi))


def test_exact_oscillator_phase_and_radial_dynamics() -> None:
    phase, error, control = 0.8, 0.1, 0.3
    reference = np.array([np.cos(phase), -np.sin(phase)])
    tangent = np.array([-np.sin(phase), -np.cos(phase)])
    normal = -reference
    normal_derivative = -tangent
    state = (1 - error) * reference
    flow = np.array([state[1], -state[0] + control])
    phase_rate = tangent @ flow / (1 + tangent @ normal_derivative * error)
    error_rate = normal @ flow
    np.testing.assert_allclose(
        tangent * phase_rate + normal_derivative * error * phase_rate + normal * error_rate,
        flow,
    )
    assert phase_rate == pytest.approx(1 - control * np.cos(phase) / (1 - error))
    assert error_rate == pytest.approx(control * np.sin(phase))


def test_proposed_nonlinear_reference_is_infeasible_in_uncontrolled_equation() -> None:
    time = np.pi / 4
    required_acceleration = -np.cos(time)
    available_acceleration = -np.cos(time) ** 3
    assert required_acceleration != pytest.approx(available_acceleration)


def test_stable_eigenvalues_allow_large_intermediate_transient_gain() -> None:
    dynamics = np.array([[-1.0, 10.0], [0.0, -1.0]])
    np.testing.assert_allclose(np.linalg.eigvals(dynamics), [-1.0, -1.0])
    assert np.linalg.norm(expm(dynamics), 2) > 3.7
    assert np.linalg.norm(expm(10 * dynamics), 2) < 0.005


def test_weighted_transition_gain_is_coordinate_invariant() -> None:
    transition = np.array([[0.8, 1.2], [0.0, 0.4]])
    scale = np.diag([10.0, 0.1])
    transformed = scale @ transition @ np.linalg.inv(scale)
    assert np.linalg.norm(transformed, 2) > 50 * np.linalg.norm(transition, 2)
    weighted = np.linalg.inv(scale) @ transformed @ scale
    assert np.linalg.norm(weighted, 2) == pytest.approx(np.linalg.norm(transition, 2))


def test_event_time_changes_impact_state_sensitivity() -> None:
    distance, speed = 4.0, 2.0
    time = distance / speed
    flow = np.array([speed, 0.0])
    normal = np.array([1.0, 0.0])
    transition = np.array([[1.0, time], [0.0, 1.0]])
    event_map = (np.eye(2) - np.outer(flow, normal) / (normal @ flow)) @ transition
    np.testing.assert_allclose(event_map, [[0.0, 0.0], [0.0, 1.0]])
    time_gradient = -normal @ transition / speed
    step = 1e-5
    numerical = ((distance - step) / speed - (distance + step) / speed) / (2 * step)
    assert numerical == pytest.approx(time_gradient[0])


def test_saltation_includes_event_timing_when_reset_is_identity() -> None:
    before, after, reset_derivative = 1.0, 2.0, 1.0
    saltation = reset_derivative + (after - reset_derivative * before) / before
    step = 1e-6
    endpoint_plus = after * (2 - (1 - step) / before)
    endpoint_minus = after * (2 - (1 + step) / before)
    assert (endpoint_plus - endpoint_minus) / (2 * step) == pytest.approx(saltation)
    assert saltation != reset_derivative


def test_positive_terminal_riccati_weight_does_not_imply_tightening() -> None:
    terminal = 0.25
    initial = np.tanh(1 + np.arctanh(terminal))
    assert initial > terminal > 0
    assert 1 / np.sqrt(terminal) > 1 / np.sqrt(initial)
    # A=0, B=Q=R=1: Sdot=S^2-1, so S decreases forward in time.
    assert initial**2 - 1 < 0


def test_linear_lyapunov_candidate_needs_nonlinear_region_check() -> None:
    for error, expected_negative in [(0.5, True), (1.5, False)]:
        derivative = 2 * error * (-error + error**3)
        assert (derivative < 0) == expected_negative


def test_multiplier_placement_requires_input_effectiveness() -> None:
    open_multiplier, target = 1.1, 0.6
    assert (open_multiplier - target) / 1.0 == pytest.approx(0.5)
    assert (open_multiplier - target) / 2.0 == pytest.approx(0.25)


@pytest.mark.parametrize(
    "relative",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch04_orbital_stability_and_transver.tex",
        "articles/motion-control/chapter4.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_orbital_editions_remove_invalid_stability_claims(relative: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    for invalid in [
        "structurally",
        "By Lyapunov's definition",
        "Numerical computation reveals the amplification",
        "guaranteed gain margin",
    ]:
        if invalid == "structurally":
            assert "structurally\nincapable" not in text
        else:
            assert invalid not in text
    assert "orbital_event_sensitivity" in text
    assert "orbital_riccati_counterexample" in text
