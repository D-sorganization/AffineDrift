"""Independent counterexamples and numerical checks for textbook issue #4264."""

import re
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm, solve_continuous_are

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion"
GRAVITY_M_S2 = 9.81
INITIAL = np.array([np.pi / 4, np.pi / 6, 2.0, -1.0])


def _point_mass_rate(state: np.ndarray, torque: float) -> np.ndarray:
    """Analytic endpoint-mass dynamics, independent of the finite-difference generator."""
    q1, q2, v1, v2 = state
    sine, cosine = np.sin(q1 - q2), np.cos(q1 - q2)
    mass = np.array([[2.0, cosine], [cosine, 1.0]])
    force = np.array(
        [
            torque - sine * v2**2 - 2 * GRAVITY_M_S2 * np.sin(q1),
            sine * v1**2 - GRAVITY_M_S2 * np.sin(q2),
        ]
    )
    return np.r_[state[2:], np.linalg.solve(mass, force)]


def _energy(states: np.ndarray) -> np.ndarray:
    q1, q2, v1, v2 = states
    return (
        v1**2
        + 0.5 * v2**2
        + np.cos(q1 - q2) * v1 * v2
        - GRAVITY_M_S2 * (2 * np.cos(q1) + np.cos(q2))
    )


@pytest.fixture(scope="module")
def trajectories() -> dict[float, np.ndarray]:
    result = {}
    for torque in (0.0, 5.0):
        solution = solve_ivp(
            lambda t, state, torque=torque: _point_mass_rate(state, torque),
            (0.0, 2.0),
            INITIAL,
            method="DOP853",
            t_eval=np.linspace(0.0, 2.0, 5),
            rtol=1e-12,
            atol=1e-14,
        )
        assert solution.success
        result[torque] = solution.y
    return result


@pytest.mark.parametrize("torque", [0.0, 5.0])
def test_independent_trajectory_obeys_work_energy(trajectories: dict, torque: float) -> None:
    states = trajectories[torque]
    energy = _energy(states)
    work = torque * (states[0] - INITIAL[0])
    np.testing.assert_allclose(energy - energy[0], work, atol=2e-10)


def test_generated_print_tables_match_independent_solver(trajectories: dict) -> None:
    source = (BOOK / "Volume_I/generated/ch07_double_pendulum.tex").read_text()
    rows = re.findall(r"^([0-2]\.\d .*?) \\\\", source, re.M)
    assert len(rows) == 10
    for offset, torque in ((0, 5.0), (5, 0.0)):
        for index in range(5):
            values = [float(value.strip()) for value in rows[offset + index].split("&")]
            np.testing.assert_allclose(values[1:5], trajectories[torque][:, index], atol=5.1e-5)


def test_actual_and_zero_torque_do_not_share_an_energy_shell(trajectories: dict) -> None:
    gap = _energy(trajectories[5.0]) - _energy(trajectories[0.0])
    assert gap[-1] == pytest.approx(-4.1854, abs=1e-4)


@pytest.mark.parametrize(("offset", "torque"), [(0, 5.0), (5, 0.0)])
def test_web_tables_match_independent_trajectory(
    trajectories: dict, offset: int, torque: float
) -> None:
    """Catch the actual prior defect: web placeholder rows diverged from the print model."""
    source = (BOOK / "quarto/ch07_counterfactuals.qmd").read_text(encoding="utf-8")
    rows = re.findall(r"^\| ([0-2]\.\d .*?) \|$", source, re.M)
    assert len(rows) == 10
    for index in range(5):
        values = [float(value.strip()) for value in rows[offset + index].split("|")]
        np.testing.assert_allclose(values[1:5], trajectories[torque][:, index], atol=5.1e-5)


def test_component_drift_ratio_is_not_monotonic(trajectories: dict) -> None:
    states = trajectories[5.0]
    ratios = []
    for state in states.T:
        drift = _point_mass_rate(state, 0.0)[2]
        control = 5.0 / (1.0 + np.sin(state[0] - state[1]) ** 2)
        ratios.append(abs(drift) / control)
    np.testing.assert_allclose(ratios, [2.079, 2.916, 1.100, 0.993, 1.602], atol=0.001)
    assert ratios[-1] < ratios[0]


@pytest.mark.parametrize("extension", ["tex", "qmd"])
def test_published_counterfactual_model_and_intervention_contract(extension: str) -> None:
    relative = (
        "Volume_I/chapters/ch07_counterfactuals.tex"
        if extension == "tex"
        else "quarto/ch07_counterfactuals.qmd"
    )
    source = (BOOK / relative).read_text(encoding="utf-8")
    assert "g_q:=\\nabla_q V" in source
    assert "fixed-time" in source and "event" in source
    assert "(eval)" not in source
    assert "\\nabla V$ is small (the state is already close" not in source
    assert "all mechanical systems" not in source


def test_short_torque_pulse_has_different_position_and_velocity_orders() -> None:
    horizon = 0.01
    acceleration = 3.0
    result = solve_ivp(lambda t, x: [x[1], acceleration], (0, horizon), [0, 0])
    np.testing.assert_allclose(
        result.y[:, -1], [acceleration * horizon**2 / 2, acceleration * horizon], atol=1e-14
    )


def test_high_speed_pendulum_has_no_quadratic_angular_drift() -> None:
    angle = 0.4
    speeds = np.array([0.0, 1.0, 100.0])
    accelerations = [-GRAVITY_M_S2 * np.sin(angle) for _ in speeds]
    np.testing.assert_allclose(accelerations, accelerations[0])
    # Cartesian radial acceleration grows, but says nothing about tangential authority.
    assert speeds[-1] ** 2 > 1000 * abs(accelerations[-1])


def test_large_orthogonal_drift_does_not_reduce_task_authority() -> None:
    drift = np.array([1000.0, 0.0])
    actuator = np.array([0.0, 1.0])
    task_gradient = np.array([0.0, 1.0])
    assert np.linalg.norm(drift) / np.linalg.norm(actuator) == 1000
    assert task_gradient @ drift == 0
    assert task_gradient @ actuator == 1


@pytest.mark.parametrize("growth", [-10.0, -1.0, 1.0, 10.0])
def test_scalar_lqr_gain_depends_on_signed_dynamics_and_cost(growth: float) -> None:
    gain = growth + np.sqrt(growth**2 + 1.0)
    independent = solve_continuous_are([[growth]], [[1.0]], [[1.0]], [[1.0]])
    assert gain == pytest.approx(independent.item())
    assert gain > 0
    assert growth - gain < 0
    if growth == 10:
        assert gain > 20


def test_hurwitz_jacobian_can_amplify_finite_time_errors() -> None:
    jacobian = np.array([[-1.0, 10.0], [0.0, -1.0]])
    assert np.all(np.linalg.eigvals(jacobian).real < 0)
    assert np.linalg.eigvalsh((jacobian + jacobian.T) / 2).max() == 4
    assert np.linalg.norm(expm(jacobian) @ [0.0, 1.0]) > 3


def test_negative_derivative_without_uniform_margin_is_not_exponential() -> None:
    # xdot=-x^3 on x>0 has f'<0 but x(t)=x0/sqrt(1+2*x0^2*t).
    time = 100.0
    exact = 1.0 / np.sqrt(1.0 + 2.0 * time)
    assert exact > np.exp(-0.1 * time)
    solution = solve_ivp(lambda t, x: -(x**3), (0, time), [1.0], rtol=1e-10, atol=1e-12)
    assert solution.y[0, -1] == pytest.approx(exact, rel=1e-8)


def test_smooth_drift_can_escape_in_finite_time() -> None:
    initial = 2.0
    time = 0.49
    exact = initial / (1 - initial * time)
    assert exact == pytest.approx(100)
    assert 1 / initial == 0.5


def test_feedback_data_can_confuse_drift_and_input() -> None:
    state = np.linspace(-2, 2, 21)
    policy = -2 * state
    observed = -state + policy
    alternative = -3 * state  # f_tilde=f+H*pi, G_tilde=G-H with H=1.
    np.testing.assert_allclose(observed, alternative)
    assert np.linalg.matrix_rank(np.column_stack([state, policy])) == 1


def test_event_time_correction_removes_false_terminal_position_effect() -> None:
    # qdot=v>0, q(T)=1. At fixed T=1/v, dq/dv=T; at the event dq/dv=0.
    velocity = 2.0
    time = 1 / velocity
    fixed_time = np.array([time, 1.0])
    rate = np.array([velocity, 0.0])
    guard = np.array([1.0, 0.0])
    event_derivative = fixed_time - rate * (guard @ fixed_time) / (guard @ rate)
    np.testing.assert_allclose(event_derivative, [0, 1])
    assert -(guard @ fixed_time) / (guard @ rate) == -1 / velocity**2
