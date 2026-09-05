"""Independent counterexamples for the motion-control introduction."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]


def _coupled_mechanics() -> tuple[np.ndarray, np.ndarray]:
    """Return a two-coordinate spring system with one applied force."""
    stiffness = np.array([[2.0, -1.0], [-1.0, 1.0]])
    dynamics = np.block([[np.zeros((2, 2)), np.eye(2)], [-stiffness, np.zeros((2, 2))]])
    return dynamics, np.array([0.0, 0.0, 1.0, 0.0])


def test_retiming_configuration_changes_state_force_and_terminal_energy() -> None:
    for duration in [1.0, 2.0]:
        phase = np.linspace(0, 1, 11)
        position = phase**2
        velocity = 2 * phase / duration
        force = 2 / duration**2
        assert position[-1] == 1.0
        assert velocity[-1] == 2 / duration
        assert 0.5 * velocity[-1] ** 2 == pytest.approx(force * position[-1])
        assert velocity[5] == 1 / duration


def test_one_input_two_coordinate_mechanics_has_four_reachable_state_directions() -> None:
    dynamics, input_map = _coupled_mechanics()
    controllability = np.column_stack(
        [np.linalg.matrix_power(dynamics, order) @ input_map for order in range(4)]
    )
    assert np.linalg.matrix_rank(controllability) == 4
    assert np.linalg.det(controllability) == pytest.approx(-1.0)


def test_unforced_curve_has_four_independent_derivatives_with_one_available_input() -> None:
    dynamics, _input_map = _coupled_mechanics()
    initial = np.array([1.0, 0.0, 0.0, 0.0])
    derivatives = np.column_stack(
        [np.linalg.matrix_power(dynamics, order) @ initial for order in range(1, 5)]
    )
    assert np.linalg.det(derivatives) == pytest.approx(-1.0)
    assert np.linalg.norm(derivatives[:, 0]) > 0.0


def test_feedforward_equation_can_be_infeasible_or_nonunique() -> None:
    input_map = np.array([[1.0], [0.0]])
    required = np.array([0.0, 1.0])
    least_squares = np.linalg.pinv(input_map) @ required
    assert np.linalg.norm(input_map @ least_squares - required) == 1.0
    redundant = np.array([[1.0, 1.0]])
    for allocation in [np.array([1.0, 0.0]), np.array([0.5, 0.5]), np.array([2.0, -1.0])]:
        np.testing.assert_allclose(redundant @ allocation, [1.0])


def test_shrinking_tube_is_not_invariant_for_constant_error() -> None:
    initial_error = 1.0
    initial_radius, radius_rate, error_rate = 1.0, -0.5, 0.0
    later_radius = initial_radius + radius_rate * 0.1
    assert initial_error > later_radius
    lyapunov_rate = 2 * initial_error * error_rate
    level_rate = 2 * initial_radius * radius_rate
    assert lyapunov_rate > level_rate


def test_robust_scalar_tube_matches_worst_case_disturbance() -> None:
    gain, disturbance_bound, initial_radius = 2.0, 0.1, 1.0
    times = np.linspace(0, 2, 51)
    radius = disturbance_bound / gain + (initial_radius - disturbance_bound / gain) * np.exp(
        -gain * times
    )
    radius_rate = -gain * (radius - disturbance_bound / gain)
    np.testing.assert_allclose(radius_rate, -gain * radius + disturbance_bound)
    for sign in [-1.0, 1.0]:
        result = solve_ivp(
            lambda _t, error, sign=sign: -gain * error + sign * disturbance_bound,
            (0, 2),
            [sign * initial_radius],
            t_eval=times,
            rtol=1e-10,
            atol=1e-12,
        )
        assert result.success
        np.testing.assert_allclose(result.y[0], sign * radius, atol=2e-10)
    assert radius[-1] > disturbance_bound / gain > 0.0


def test_tracking_is_regulation_of_a_time_dependent_error() -> None:
    for time, error in [(0.2, 0.3), (0.7, -0.5)]:
        reference, reference_rate, gain = np.sin(time), np.cos(time), 2.0
        state = reference + error
        control = reference_rate - reference - (gain + 1) * error
        error_rate = state + control - reference_rate
        assert error_rate == pytest.approx(-gain * error)


def test_metric_transport_preserves_distance_after_changing_units() -> None:
    error = np.array([0.2, 3.0])
    metric = np.diag([4.0, 0.25])
    units = np.diag([100.0, 1.0])
    transformed_metric = np.linalg.inv(units).T @ metric @ np.linalg.inv(units)
    assert (units @ error) @ transformed_metric @ (units @ error) == pytest.approx(
        error @ metric @ error
    )
    assert np.linalg.norm(units @ error) != pytest.approx(np.linalg.norm(error))


def test_orbit_stabilizer_has_no_nominal_feedforward_requirement() -> None:
    gain = 0.7
    for position, velocity in [(1.2, 0.4), (0.5, -0.3), (1.0, 0.0)]:
        radius_squared = position**2 + velocity**2
        control = gain * velocity * (1 - radius_squared)
        radius_squared_rate = 2 * position * velocity + 2 * velocity * (-position + control)
        lyapunov_rate = 0.5 * (radius_squared - 1) * radius_squared_rate
        assert lyapunov_rate == pytest.approx(-gain * velocity**2 * (radius_squared - 1) ** 2)
    phase = np.linspace(0, 2 * np.pi, 20)
    np.testing.assert_allclose(
        gain * np.sin(phase) * (1 - np.cos(phase) ** 2 - np.sin(phase) ** 2), 0, atol=1e-15
    )


@pytest.mark.parametrize(
    "edition",
    [
        "articles/motion-control/chapter1.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch01_throwing_away_the_target.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_opening_chapter_excludes_invalid_motion_foundations(edition: str) -> None:
    text = (ROOT / edition).read_text(encoding="utf-8")
    for phrase in [
        "approximately 90\\%",
        "at most $2m$ in the $2n$-dimensional state space",
        "trajectory-centric replacement for Lyapunov stability",
        "centrifugal acceleration of the downswing \\emph{automatically}",
    ]:
        assert phrase not in text


def test_web_path_timing_preserves_second_derivative_primes() -> None:
    text = (ROOT / "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd").read_text(
        encoding="utf-8"
    )
    introduction = text.split("## Curves in State Space", 1)[0]
    assert introduction.count("q_d" + chr(39) * 2) == 2
    assert 'q_d"' not in introduction
