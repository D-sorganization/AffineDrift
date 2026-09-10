"""Independent counterexamples for the paired motor-learning chapter."""

from pathlib import Path

import numpy as np
import pytest

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"
EDITIONS = [BOOK / "chapters/ch25_motor_learning.tex", BOOK / "quarto/ch25_motor_learning.qmd"]
GRAVITY_M_S2 = 9.81


def test_task_success_can_coexist_with_sensory_prediction_error() -> None:
    hand, rotation, target, predicted_cursor = -45.0, 45.0, 0.0, -45.0
    observed_cursor = hand + rotation
    assert target - observed_cursor == 0
    assert observed_cursor - predicted_cursor == 45


@pytest.mark.parametrize("reward, expected, error", [(1, 1, 0), (1, 0.25, 0.75), (0, 0.75, -0.75)])
def test_terminal_reward_prediction_is_not_reward(
    reward: float, expected: float, error: float
) -> None:
    assert reward - expected == pytest.approx(error)


def test_discounted_prediction_is_consistent_across_time() -> None:
    gamma, future_value = 0.9, 1.0
    current_value = gamma * future_value
    assert 0 + gamma * future_value - current_value == 0


@pytest.mark.parametrize("gain, ratio", [(0.25, 0.75), (1.5, -0.5), (2.1, -1.1)])
def test_trial_update_agrees_with_closed_form(gain: float, ratio: float) -> None:
    response = 0.0
    errors = []
    for _ in range(7):
        errors.append(4 - response)
        response += gain * (4 - response)
    np.testing.assert_allclose(errors, 4 * ratio ** np.arange(7), atol=2e-14)


def test_forgetting_leaves_a_nonzero_steady_error() -> None:
    response = 0.0
    for _ in range(400):
        response = 0.98 * response + 0.25 * (4 - response)
    assert 4 - response == pytest.approx(8 / 27)


def test_measurement_update_and_uncertainty_are_distinct() -> None:
    # Minimize the quadratic likelihood rather than calling a Kalman routine.
    prior, observation, prior_variance, noise_variance = 20.0, 22.0, 9.0, 1.0
    precision = 1 / prior_variance + 1 / noise_variance
    mean = (prior / prior_variance + observation / noise_variance) / precision
    assert mean == pytest.approx(21.8)
    assert 1 / precision == pytest.approx(0.9)


def test_less_joint_variation_can_mean_more_task_variation() -> None:
    joint_covariances = [np.array([[1, 0.9], [0.9, 1]]), np.array([[4, -3.8], [-3.8, 4]])]
    endpoint_variances = []
    # Exact four-point distributions independently realize each covariance.
    for covariance in joint_covariances:
        values, vectors = np.linalg.eigh(covariance)
        assert np.all(values > 0)
        samples = vectors @ np.diag(np.sqrt(2 * values))
        samples = np.concatenate([samples, -samples], axis=1).T
        np.testing.assert_allclose(samples.T @ samples / 4, covariance, atol=1e-14)
        endpoint_variances.append(np.mean(np.sum(samples, axis=1) ** 2))
    np.testing.assert_allclose(endpoint_variances, [3.8, 0.4], atol=1e-14)
    assert np.trace(joint_covariances[0]) < np.trace(joint_covariances[1])
    assert endpoint_variances[0] > endpoint_variances[1]


def test_task_bias_adds_to_dispersion() -> None:
    errors = 2 + np.array([-1, 1])
    assert np.mean(errors**2) == 5
    assert np.var(errors) == 1


def test_null_direction_depends_on_the_task() -> None:
    motion = np.array([1.0, -1.0])
    assert np.array([1.0, 1.0]) @ motion == 0
    assert np.array([1.0, 2.0]) @ motion == -1


def test_vacuum_range_requires_square_root_speed_scaling() -> None:
    g, angle = GRAVITY_M_S2, np.pi / 4
    ranges = np.array([20.0, 80.0])
    speeds = np.sqrt(ranges * g / np.sin(2 * angle))
    assert speeds[1] / speeds[0] == pytest.approx(2)
    np.testing.assert_allclose(speeds**2 * np.sin(2 * angle) / g, ranges)


@pytest.mark.parametrize("weekly, years", [(10, 250 / 13), (20, 125 / 13)])
def test_practice_hour_arithmetic(weekly: float, years: float) -> None:
    assert 10000 / (52 * weekly) == pytest.approx(years)
    assert 10 * 52 * 10 == 5200


def test_success_rate_uncertainty_does_not_vanish_after_one_good_shot() -> None:
    # Wilson interval for 8 successes / 10 independent Bernoulli attempts.
    n, p, z = 10, 0.8, 1.96
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    half_width = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    np.testing.assert_allclose(
        [center - half_width, center + half_width], [0.49015685, 0.94331905], atol=1e-8
    )


@pytest.mark.parametrize("path", EDITIONS, ids=["print", "web"])
def test_false_mechanisms_and_universal_practice_claims_are_removed(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for claim in [
        "applies perfectly",
        "why mechanics don't matter",
        "why random practice is better",
        "karl sch",
        "the complete proprioceptive trajectory",
        "the actual sensory target",
        "ball lands about 150",
        "70\\% of all brain neurons",
        "70% of all brain neurons",
    ]:
        assert claim not in text


@pytest.mark.parametrize("path", EDITIONS, ids=["print", "web"])
def test_numerical_argument_and_learning_tests_are_present(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in [
        "sensory prediction error",
        "reward prediction error",
        "retention",
        "transfer",
        "3.8",
        "0.4",
        "19.23",
        "worked answers",
    ]:
        assert term in text
