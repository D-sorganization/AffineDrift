"""Independent counterexamples for learning, identification, and controller reuse."""

from itertools import product
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]


def test_lifted_error_recursion_preserves_dynamics_and_error_sign() -> None:
    plant = np.array([[1.0, 0.0], [0.5, 1.0], [0.2, 0.5]])
    learning = np.array([[0.1, 0.2, 0.0], [0.0, 0.1, 0.2]])
    command = np.array([0.3, -0.2])
    disturbance = np.array([0.1, 0.2, -0.1])
    reference = np.array([1.0, 0.5, 0.4])
    error = reference - plant @ command - disturbance
    updated = command + learning @ error
    assert reference - plant @ updated - disturbance == pytest.approx(
        (np.eye(3) - plant @ learning) @ error
    )


def test_spectral_stability_does_not_imply_monotone_trial_improvement() -> None:
    transition = np.array([[0.5, 4.0], [0.0, 0.5]])
    initial = np.array([0.0, 1.0])
    assert max(abs(np.linalg.eigvals(transition))) == 0.5
    assert np.linalg.norm(transition @ initial) > 4 * np.linalg.norm(initial)
    assert np.linalg.norm(np.linalg.matrix_power(transition, 100) @ initial) < 1e-20


@pytest.mark.parametrize(("learning", "ratio"), [(0.25, 0.5), (1.2, -1.4)])
def test_actual_scalar_gain_determines_trial_convergence(learning: float, ratio: float) -> None:
    command, reference = 0.0, 1.0
    errors = []
    for _trial in range(12):
        error = reference - 2 * command
        errors.append(error)
        command += learning * error
    assert np.array(errors[1:]) == pytest.approx(ratio * np.array(errors[:-1]))
    assert (abs(errors[-1]) < abs(errors[0])) == (abs(ratio) < 1)


def test_rank_deficient_output_map_leaves_unlearnable_error() -> None:
    plant = np.array([[1.0], [2.0]])
    learning = np.linalg.pinv(plant)
    inaccessible = np.array([2.0, -1.0])
    assert (np.eye(2) - plant @ learning) @ inaccessible == pytest.approx(inaccessible)
    assert max(abs(np.linalg.eigvals(np.eye(2) - plant @ learning))) == pytest.approx(1)


def test_filter_converges_to_a_biased_tracking_solution() -> None:
    command, reference = 0.0, 1.0
    for _trial in range(100):
        command = 0.8 * (command + 0.25 * (reference - 2 * command))
    assert command == pytest.approx(reference / 3)
    assert reference - 2 * command == pytest.approx(reference / 3)


@pytest.mark.parametrize("learning", [0.1, 0.5, 1.0, 1.9])
def test_independent_noise_accumulates_to_the_stated_stationary_variance(learning: float) -> None:
    measurement_variance = 0.3
    impulse_coefficients = learning * (1 - learning) ** np.arange(1000)
    independent_sum = measurement_variance * (impulse_coefficients @ impulse_coefficients)
    stationary = learning * measurement_variance / (2 - learning)
    assert independent_sum == pytest.approx(stationary)
    assert stationary == pytest.approx(
        (1 - learning) ** 2 * stationary + learning**2 * measurement_variance
    )


def test_exact_tracking_does_not_resolve_indistinguishable_parameters() -> None:
    inputs = np.linspace(-2, 2, 11)
    regressor = np.column_stack([inputs, inputs])
    first, second = np.array([1.0, 2.0]), np.array([-4.0, 7.0])
    assert np.linalg.matrix_rank(regressor) == 1
    assert regressor @ first == pytest.approx(regressor @ second)
    assert np.dot([1 / 3, 1 / 3], first) == pytest.approx(1)
    assert np.dot([1 / 3, 1 / 3], second) == pytest.approx(1)


def test_likelihood_ratio_gradient_matches_exact_finite_horizon_return() -> None:
    theta = 0.4

    def objective(parameter: float) -> float:
        probability = 1 / (1 + np.exp(-parameter))
        return probability + 2 * probability**2

    probability = 1 / (1 + np.exp(-theta))
    gradient = 0.0
    for first, second in product((0, 1), repeat=2):
        mass = probability ** (first + second) * (1 - probability) ** (2 - first - second)
        first_reward, second_reward = first, 2 * first * second
        gradient += mass * (
            (first - probability) * (first_reward + second_reward)
            + (second - probability) * second_reward
        )
    step = 1e-5
    finite_difference = (objective(theta + step) - objective(theta - step)) / (2 * step)
    assert gradient == pytest.approx(finite_difference, rel=1e-9)


def test_finite_quadratic_penalty_does_not_enforce_upper_bound() -> None:
    penalty = 2.0
    result = minimize_scalar(lambda control: -(control - penalty * max(0, control - 1) ** 2))
    assert result.success
    assert result.x == pytest.approx(1 + 1 / (2 * penalty))
    assert result.x > 1


def test_averaging_stable_controllers_can_be_unstable() -> None:
    first = np.array([[-1.0, 4.0], [0.0, -1.0]])
    second = first.T
    average = (first + second) / 2
    assert max(np.linalg.eigvals(first).real) < 0
    assert max(np.linalg.eigvals(second).real) < 0
    assert sorted(np.linalg.eigvals(average)) == pytest.approx([-3, 1])
    direction = np.array([1.0, 1.0]) / np.sqrt(2)
    assert np.linalg.norm(expm(average) @ direction) == pytest.approx(np.e)


def test_average_of_feasible_paths_can_intersect_an_obstacle() -> None:
    parameter = np.linspace(0, 1, 1001)
    upper = np.column_stack([parameter, np.sin(np.pi * parameter)])
    lower = np.column_stack([parameter, -np.sin(np.pi * parameter)])
    obstacle_center, obstacle_radius = np.array([0.5, 0.0]), 0.25
    assert np.min(np.linalg.norm(upper - obstacle_center, axis=1)) > obstacle_radius
    assert np.min(np.linalg.norm(lower - obstacle_center, axis=1)) > obstacle_radius
    average = (upper + lower) / 2
    assert np.min(np.linalg.norm(average - obstacle_center, axis=1)) == 0


def test_common_quadratic_certificate_can_support_convex_blending() -> None:
    first = np.array([[-1.0, 0.5], [-0.2, -2.0]])
    second = np.array([[-2.0, -0.2], [0.5, -1.0]])
    metric = np.diag([1.0, 1.5])
    for weight in np.linspace(0, 1, 21):
        average = weight * first + (1 - weight) * second
        derivative = average.T @ metric + metric @ average
        endpoints = weight * (first.T @ metric + metric @ first) + (1 - weight) * (
            second.T @ metric + metric @ second
        )
        assert derivative == pytest.approx(endpoints)
        assert max(np.linalg.eigvalsh(derivative)) < 0


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch10_learning_to_move.tex",
        "articles/motion-control/chapter10.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_all_editions_separate_learning_identification_and_certification(source: str) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    if source.endswith(".qmd"):
        text = text.split("## Learning to Move", 1)[1].split("## Case Study:", 1)[0]
    else:
        text = text.split(r"\chapter{Learning to Move}", 1)[1].split(r"\chapter{Case Study:", 1)[0]
    for required in [
        r"e_{j+1}=(I_p-GL)e_j",
        "stationary command variance",
        "indistinguishable",
        "common certificate",
        "initial guess",
        "held-out",
        "Bristow",
    ]:
        assert required in text
    for incorrect in [
        "true orbit boundary",
        "persistently excite the full Lie algebra",
        "organically converges",
        "instantly generate a stable, feasible motion",
        "remove non-repeatable sensor noise",
        "perfects the funnel",
    ]:
        assert incorrect not in text
