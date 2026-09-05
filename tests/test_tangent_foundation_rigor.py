"""Independent counterexamples for derivatives, flow transport and sensitivities."""

from math import cos, exp, expm1, sin
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import OdeSolution, quad, solve_ivp
from scipy.linalg import expm

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
)


def test_continuous_derivative_does_not_imply_quadratic_remainder() -> None:
    amplitudes = np.array([1e-2, 1e-4, 1e-6])
    remainder = amplitudes**1.5
    assert np.all(np.diff(remainder / amplitudes) < 0)
    assert remainder / amplitudes**2 == pytest.approx([10, 100, 1000])


def test_directional_derivatives_need_not_form_a_linear_map() -> None:
    def directional(a: float, b: float) -> float:
        return a**3 / (a * a + b * b)

    assert directional(1, 1) == pytest.approx(0.5)
    assert directional(1, 0) + directional(0, 1) == pytest.approx(1.0)


def test_flat_space_flow_is_not_additive() -> None:
    duration = 0.2

    def flow(initial: float) -> float:
        return initial / (1 - duration * initial)

    assert flow(2) != pytest.approx(2 * flow(1))
    step = 1e-6
    derivative = (flow(1 + step) - flow(1 - step)) / (2 * step)
    assert derivative == pytest.approx((1 - duration) ** -2, rel=1e-9)
    assert derivative != pytest.approx(1.0)  # Euclidean parallel transport.


def test_finite_perturbation_error_survives_exact_integration() -> None:
    duration, initial, amplitude = 0.2, 1.0, 0.1
    denominator = 1 - duration * initial
    exact = (initial + amplitude) / (denominator - duration * amplitude)
    linear = initial / denominator + amplitude / denominator**2
    error = duration * amplitude**2 / (denominator**2 * (denominator - duration * amplitude))
    assert exact - linear == pytest.approx(error)
    assert error == pytest.approx(0.004006410256410256)


def test_coordinate_jacobian_includes_moving_basis_term() -> None:
    # x_dot=1, y=x^2 on x>0: A_x=0, A_y=1/x.
    initial, duration, variation = 1.0, 0.5, 0.01
    x = initial + duration
    transform, transform_rate = 2 * x, 2.0
    a_y = (transform_rate + transform * 0.0) / transform
    assert a_y == pytest.approx(1 / x)
    phi_y = x / initial
    assert phi_y * (2 * initial * variation) == pytest.approx(2 * x * variation)


def test_pendulum_energy_supplies_the_missing_stability_argument() -> None:
    # Nondimensional time, energy divided by m*g*L.
    initial = np.array([0.2, 0.0])

    def dynamics(_time: float, state: np.ndarray) -> np.ndarray:
        return np.array([state[1], -sin(state[0])])

    solution = solve_ivp(dynamics, (0, 12), initial, rtol=1e-11, atol=1e-12)
    energy = 0.5 * solution.y[1] ** 2 + 1 - np.cos(solution.y[0])
    assert energy == pytest.approx(1 - cos(initial[0]), abs=1e-10)
    assert np.max(np.abs(solution.y[0])) <= 0.2 + 1e-10
    assert np.max(energy) > 0.01


def test_same_imaginary_linearization_has_opposite_radial_stability() -> None:
    initial, duration = 0.1, 10.0
    stable_radius = initial / np.sqrt(1 + 2 * initial**2 * duration)
    unstable_radius = initial / np.sqrt(1 - 2 * initial**2 * duration)
    assert stable_radius < initial < unstable_radius
    rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    assert np.sort_complex(np.linalg.eigvals(rotation)) == pytest.approx([-1j, 1j])


def test_affine_input_superposition_uses_rate_increments() -> None:
    drift, gain, nominal, first, second = 2.0, 3.0, 0.4, 0.1, 0.2

    def rate(input_value: float) -> float:
        return drift + gain * input_value

    combined = rate(nominal + first + second) - rate(nominal)
    increments = rate(nominal + first) + rate(nominal + second) - 2 * rate(nominal)
    assert combined == pytest.approx(increments)
    assert (first + second) ** 2 != pytest.approx(first**2 + second**2)


def test_time_varying_transport_is_ordered() -> None:
    first = np.array([[0.0, 1.0], [0.0, 0.0]])
    second = first.T
    ordered = expm(second) @ expm(first)
    assert ordered == pytest.approx(np.array([[1.0, 1.0], [1.0, 2.0]]))
    assert not np.allclose(ordered, expm(first + second))
    assert not np.allclose(ordered, expm(first) @ expm(second))


def test_input_kernel_requires_a_duration_or_integral() -> None:
    terminal, start, height = 1.0, 0.3, 0.2
    kernel = exp(-(terminal - start))
    durations = np.array([1e-2, 1e-3, 1e-4])
    responses = height * kernel * np.expm1(durations)
    assert np.all(np.diff(np.abs(responses / (height * durations) - kernel)) < 0)
    assert responses[-1] == pytest.approx(9.932202676960212e-6)


def test_endpoint_derivative_acts_on_an_entire_input_direction() -> None:
    terminal = 1.0
    constant, _ = quad(lambda t: exp(-(terminal - t)), 0, terminal)
    ramp, _ = quad(lambda t: exp(-(terminal - t)) * t, 0, terminal)
    assert constant == pytest.approx(-expm1(-terminal))
    assert ramp == pytest.approx(terminal + expm1(-terminal))
    assert constant != pytest.approx(ramp)


def test_adjoint_gradient_matches_independent_nonlinear_rollouts() -> None:
    terminal, initial, nominal, control_weight = 0.3, 0.2, 0.4, 0.1

    def rollout(amplitude: float) -> tuple[float, OdeSolution]:
        def dynamics(time: float, state: np.ndarray) -> np.ndarray:
            control = nominal + amplitude * (1 + time)
            return np.array(
                [state[0] ** 2 + control, 0.5 * (state[0] ** 2 + control_weight * control**2)]
            )

        solution = solve_ivp(
            dynamics,
            (0, terminal),
            [initial, 0],
            dense_output=True,
            rtol=1e-11,
            atol=1e-12,
        )
        cost = 0.5 * solution.y[0, -1] ** 2 + solution.y[1, -1]
        assert solution.success and solution.sol is not None
        return float(cost), solution.sol

    _, state = rollout(0)

    def adjoint(time: float, costate: np.ndarray) -> np.ndarray:
        x = state(time)[0]
        return np.array([-2 * x * costate[0] - x])

    backward = solve_ivp(
        adjoint,
        (terminal, 0),
        [state(terminal)[0]],
        dense_output=True,
        rtol=1e-11,
        atol=1e-12,
    )
    gradient, _ = quad(
        lambda t: (backward.sol(t)[0] + control_weight * nominal) * (1 + t),
        0,
        terminal,
    )
    step = 1e-5
    numerical = (rollout(step)[0] - rollout(-step)[0]) / (2 * step)
    assert gradient == pytest.approx(numerical, rel=1e-8)


def test_feedback_sensitivity_uses_the_closed_loop_derivative() -> None:
    # x_dot=x+u, u=-2x: perturbing the initial state while retaining the policy.
    assert exp((1 - 2) * 1.0) == pytest.approx(exp(-1))
    assert exp(1.0) / exp(-1.0) > 7.0


def test_work_adds_on_the_combined_motion_not_separate_motions() -> None:
    # Unit mass, two unit forces, unit duration, initial velocity zero.
    each_combined, _ = quad(lambda t: 2 * t, 0, 1)
    each_separate, _ = quad(lambda t: t, 0, 1)
    assert 2 * each_combined == pytest.approx(0.5 * 2**2)
    assert 2 * each_separate == pytest.approx(1.0)


@pytest.mark.parametrize(
    "required,forbidden",
    [
        ("A Tangent Space Is Not a Derivative", "it is the Fréchet derivative"),
        (
            "Continuous Differentiability Does Not Give a Quadratic Bound",
            "minimum requirement for the existence of derivatives",
        ),
        ("Flow Transport Is Not Parallel Transport", "Nonlinearity as Tangent Space Variation"),
        ("An Input Kernel Is a Density", r"\frac{\partial x(t_1)}{\partial u(\cdot)} = \int"),
        (
            "The Policy Determines the Sensitivity",
            "Complex systems are just a series of simple linear moments",
        ),
        ("Separate the Two Refinement Experiments", "*[To be added:"),
    ],
)
def test_reference_states_the_missing_foundational_conditions(
    required: str,
    forbidden: str,
) -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert required in source
    assert forbidden not in source
