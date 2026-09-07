"""Check the reader's variational examples against independent identities."""

import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion"
WEB = ROOT / "quarto/ch02_variational.qmd"
PRINT = ROOT / "Volume_I/chapters/ch02_variational.tex"
GRAVITY_M_S2 = 10.0


@pytest.fixture(scope="module")
def example() -> dict[str, Any]:
    """Execute the same complete program supplied in both editions."""
    text = WEB.read_text(encoding="utf-8")
    match = re.search(r"```python\n(# Variational chapter example\n.*?)\n```", text, re.S)
    assert match is not None, "Publish the independently checkable chapter example"
    code = match[1]
    assert code in PRINT.read_text(encoding="utf-8")
    namespace: dict[str, Any] = {}
    exec(compile(code, str(WEB), "exec"), namespace)
    return namespace


@pytest.mark.parametrize("time", [0.0, 0.25, 0.5, 1.25])
def test_pendulum_transition_matches_matrix_ode(example: dict[str, Any], time: float) -> None:
    matrix = np.array([[0.0, 1.0], [-GRAVITY_M_S2, 0.0]])
    actual = example["pendulum_stm"](time)
    np.testing.assert_allclose(actual, expm(matrix * time), atol=1e-13)
    assert np.linalg.det(actual) == pytest.approx(1.0, abs=1e-13)


def test_pendulum_initial_and_impulse_responses(example: dict[str, Any]) -> None:
    matrix = np.array([[0.0, 1.0], [-GRAVITY_M_S2, 0.0]])
    initial = np.array([0.1, 0.0])
    solution = solve_ivp(
        lambda _, state: matrix @ state, [0.0, 0.5], initial, rtol=1e-11, atol=1e-13
    )
    np.testing.assert_allclose(example["initial_response"], solution.y[:, -1], atol=1e-11)
    np.testing.assert_allclose(
        example["impulse_response"], expm(matrix * 0.25) @ np.array([0.0, 1.0]), atol=1e-13
    )


def test_qr_accumulates_noncommuting_intervals_on_left(example: dict[str, Any]) -> None:
    intervals = [
        np.array([[1.0, 2.0], [0.0, 1.0]]),
        np.array([[1.0, 0.0], [3.0, 1.0]]),
        np.array([[0.8, -0.3], [0.4, 1.2]]),
    ]
    orthogonal, triangular = example["qr_product"](intervals)
    expected = intervals[2] @ intervals[1] @ intervals[0]
    np.testing.assert_allclose(orthogonal @ triangular, expected, atol=1e-13)
    np.testing.assert_allclose(orthogonal.T @ orthogonal, np.eye(2), atol=1e-13)


def test_zoh_singular_double_integrator(example: dict[str, Any]) -> None:
    interval = 0.3
    matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    channel = np.array([[0.0], [1.0]])
    transition, sensitivity = example["zoh"](matrix, channel, interval)
    np.testing.assert_allclose(transition, [[1.0, interval], [0.0, 1.0]], atol=1e-14)
    np.testing.assert_allclose(sensitivity, [[interval**2 / 2], [interval]], atol=1e-14)


def test_joint_remainder_retains_input_state_cross_term(example: dict[str, Any]) -> None:
    nominal, command, displacement, increment = 0.3, 0.7, 0.2, -0.1

    def field(state: float, control: float) -> float:
        return state**2 + (1 + state) * control

    exact = field(nominal + displacement, command + increment) - field(nominal, command)
    linear = (2 * nominal + command) * displacement + (1 + nominal) * increment
    assert example["joint_remainder"](displacement, increment) == pytest.approx(exact - linear)
    assert example["joint_remainder"](displacement, 0.0) == pytest.approx(displacement**2)


def test_adjoint_includes_parameter_dependent_initial_state(example: dict[str, Any]) -> None:
    parameter, terminal = 0.4, 0.7

    def objective(value: float) -> float:
        solution = solve_ivp(
            lambda _, state: value * state,
            [0.0, terminal],
            [value],
            rtol=1e-12,
            atol=1e-14,
            dense_output=True,
        )
        assert solution.sol is not None
        running = quad(lambda time: 0.5 * solution.sol(time)[0] ** 2, 0.0, terminal)[0]
        return float(0.5 * solution.y[0, -1] ** 2 + running)

    increment = 1e-5
    finite_difference = (objective(parameter + increment) - objective(parameter - increment)) / (
        2 * increment
    )
    assert example["scalar_adjoint_gradient"](parameter, terminal) == pytest.approx(
        finite_difference, rel=1e-8, abs=1e-9
    )


def test_volume_shrinkage_does_not_bound_trajectory_separation() -> None:
    transition = expm(np.diag([1.0, -2.0]))
    assert np.linalg.det(transition) < 1.0
    assert np.linalg.norm(transition @ np.array([1.0, 0.0])) > 1.0


def test_symplectic_euler_can_be_unstable(example: dict[str, Any]) -> None:
    stable = example["symplectic_euler_matrix"](0.5)
    unstable = example["symplectic_euler_matrix"](3.0)
    symplectic = np.array([[0.0, 1.0], [-1.0, 0.0]])
    for matrix in [stable, unstable]:
        np.testing.assert_allclose(matrix.T @ symplectic @ matrix, symplectic, atol=1e-14)
    assert max(abs(np.linalg.eigvals(stable))) == pytest.approx(1.0)
    assert max(abs(np.linalg.eigvals(unstable))) > 1.0


def test_rotating_hurwitz_spectrum_has_growing_flow() -> None:
    """Compare the rotating-frame derivation with a direct time-varying ODE."""
    frozen = np.array([[-1.0, 4.0], [0.0, -1.0]])
    rotation_rate = np.array([[0.0, 1.0], [-1.0, 0.0]])
    initial = np.array([np.sqrt(3.0), 1.0])

    def derivative(time: float, state: np.ndarray) -> np.ndarray:
        rotation = expm(rotation_rate * time)
        matrix = rotation @ frozen @ rotation.T
        np.testing.assert_allclose(np.linalg.eigvals(matrix).real, -1.0, atol=1e-6)
        return matrix @ state

    terminal = 2.0
    solution = solve_ivp(derivative, [0.0, terminal], initial, rtol=1e-10, atol=1e-12)
    expected = expm(rotation_rate * terminal) @ expm((frozen - rotation_rate) * terminal)
    np.testing.assert_allclose(solution.y[:, -1], expected @ initial, atol=1e-8)
    assert np.linalg.norm(solution.y[:, -1]) > np.linalg.norm(initial)


@pytest.mark.parametrize("source", [WEB, PRINT])
def test_published_pendulum_tables_match_independent_exponential(source: Path) -> None:
    """Protect actual displayed values, including the formerly wrong factor of ten."""
    text = source.read_text(encoding="utf-8")
    matrix = np.array([[0.0, 1.0], [-GRAVITY_M_S2, 0.0]])
    separator = r"\s*\|\s*" if source.suffix == ".qmd" else r"\s*&\s*"
    for time in [0.25, 0.5]:
        row = re.search(rf"{time:.2f}" + separator + r"([^\n]+)", text)
        assert row is not None
        numbers = re.findall(r"-?\d+\.\d+", row[1])
        np.testing.assert_allclose(
            np.array(numbers[:4], dtype=float), expm(matrix * time).ravel(), atol=5.1e-7
        )
    for label, expected in [
        ("Initial Angle", expm(matrix * 0.5) @ np.array([0.1, 0.0])),
        ("Torque Impulse", expm(matrix * 0.25) @ np.array([0.0, 1.0])),
    ]:
        row = re.search(label + separator + r"([^\n]+)", text)
        assert row is not None
        numbers = re.findall(r"-?\d+\.\d+", row[1])
        np.testing.assert_allclose(np.array(numbers[:2], dtype=float), expected, atol=5.1e-7)
