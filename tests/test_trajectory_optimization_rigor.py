"""Reproducible checks for optimization and uncertainty claims in four editions."""

from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]


def test_normalized_time_scales_dynamics_and_cost_in_same_direction() -> None:
    duration, speed = 3.0, 2.0
    normalized_derivative = duration * speed
    assert normalized_derivative == 6.0
    assert duration * normalized_derivative != speed
    physical_cost = quad(lambda _t: speed**2 / 2, 0, duration)[0]
    normalized_cost = duration * quad(lambda _s: speed**2 / 2, 0, 1)[0]
    assert physical_cost == pytest.approx(normalized_cost)


def test_free_time_effort_infimum_needs_duration_control() -> None:
    distance, rho = 2.0, 0.5
    durations = np.array([1.0, 2.0, 4.0, 8.0])
    energy = distance**2 / (2 * durations)
    assert np.all(np.diff(energy) < 0)
    optimum = distance / np.sqrt(2 * rho)
    result = minimize_scalar(
        lambda t: distance**2 / (2 * t) + rho * t, bounds=(0.1, 10), method="bounded"
    )
    assert result.success
    assert result.x == pytest.approx(optimum, rel=1e-5)


def test_minimization_hamiltonian_has_correct_control_sign() -> None:
    costate = -2.0
    controls = np.linspace(-3, 3, 601)
    hamiltonian = controls**2 / 2 + costate * controls
    assert controls[np.argmin(hamiltonian)] == pytest.approx(-costate)
    assert controls[np.argmax(hamiltonian)] != -costate


def test_rest_to_rest_cubic_satisfies_endpoint_and_energy_conditions() -> None:
    distance, duration = 2.0, 3.0
    velocity_end = quad(
        lambda t: 6 * distance / duration**2 * (1 - 2 * t / duration), 0, duration
    )[0]
    position_end = quad(
        lambda t: (duration - t) * 6 * distance / duration**2 * (1 - 2 * t / duration), 0, duration
    )[0]
    effort = quad(
        lambda t: (6 * distance / duration**2 * (1 - 2 * t / duration)) ** 2 / 2, 0, duration
    )[0]
    assert velocity_end == pytest.approx(0, abs=1e-12)
    assert position_end == pytest.approx(distance)
    assert effort == pytest.approx(6 * distance**2 / duration**3)


def test_arrival_speed_and_rest_to_rest_have_different_torque_patterns() -> None:
    distance, acceleration = 2.0, 1.0
    arrival_time = np.sqrt(2 * distance / acceleration)
    assert acceleration * arrival_time**2 / 2 == pytest.approx(distance)
    assert acceleration * arrival_time == pytest.approx(2.0)
    rest_time = 2 * np.sqrt(distance / acceleration)
    half = rest_time / 2
    first_distance = acceleration * half**2 / 2
    second_distance = acceleration * half**2 - acceleration * half**2 / 2
    assert first_distance + second_distance == pytest.approx(distance)
    assert acceleration * half - acceleration * half == 0


def test_hermite_simpson_matches_cubic_rest_to_rest_motion() -> None:
    duration = 2.0
    x0, x1 = np.array([0.0, 0.0]), np.array([1.0, 0.0])
    f0, f1 = np.array([0.0, 1.5]), np.array([0.0, -1.5])
    midpoint = (x0 + x1) / 2 + duration * (f0 - f1) / 8
    np.testing.assert_allclose(midpoint, [0.5, 0.75])
    fc = np.array([midpoint[1], 0.0])
    np.testing.assert_allclose(x1 - x0 - duration * (f0 + 4 * fc + f1) / 6, 0)


def test_node_feasibility_does_not_bound_intermediate_constraint() -> None:
    nodes = np.array([0.0, 0.5, 1.0])
    # An unsampled oscillation can vanish at every collocation/sample point.
    residual_at_nodes = nodes * (nodes - 0.5) * (nodes - 1)
    np.testing.assert_allclose(residual_at_nodes, 0)
    assert 0.25 * (0.25 - 0.5) * (0.25 - 1) != 0
    endpoint_positions = 4 * nodes[[0, 2]] * (1 - nodes[[0, 2]])
    assert np.all(endpoint_positions <= 0.5)
    assert 4 * nodes[1] * (1 - nodes[1]) > 0.5


def test_distal_angular_velocity_does_not_determine_tip_speed() -> None:
    aligned_jacobian = np.array([[1.0, 1.0], [0.0, 0.0]])
    assert np.linalg.norm(aligned_jacobian @ np.array([-1.0, 1.0])) == 0
    assert np.linalg.norm(aligned_jacobian @ np.array([1.0, 1.0])) == 2


def test_condition_number_does_not_measure_absolute_amplification() -> None:
    small, large = np.eye(2), 1000 * np.eye(2)
    assert np.linalg.cond(small) == np.linalg.cond(large) == 1
    assert np.linalg.norm(large, 2) / np.linalg.norm(small, 2) == 1000


def test_output_loss_includes_bias_as_well_as_covariance() -> None:
    mean = np.array([2.0, -1.0])
    covariance = np.diag([0.25, 1.0])
    weight = np.diag([1.0, 2.0])
    total = mean @ weight @ mean + np.trace(weight @ covariance)
    assert total == pytest.approx(8.25)
    assert total > np.trace(weight @ covariance)


def test_multiplicative_noise_changes_covariance_even_with_zero_mean() -> None:
    state = np.array([-1.0, 1.0])[:, None]
    noise = np.array([-1.0, 1.0])[None, :]
    a, n, g = 0.5, 0.2, 0.1
    propagated = a * state + n * state * noise + g * noise
    assert propagated.mean() == pytest.approx(0)
    assert propagated.var() == pytest.approx(a**2 + n**2 + g**2)
    assert propagated.var() > a**2 + g**2


def test_marginal_chance_constraint_does_not_give_joint_same_probability() -> None:
    marginal = norm.cdf(norm.ppf(0.95))
    assert marginal == pytest.approx(0.95)
    assert marginal**10 < 0.60
    assert 1 - 10 * 0.005 == 0.95


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch06_trajectory_optimization.tex",
        "articles/motion-control/chapter6.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_all_editions_state_valid_optimization_and_uncertainty_conditions(source: str) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    if source.endswith("volume2_content.qmd"):
        text = text.split("## Trajectory Optimization", 1)[1].split("## Funnel Synthesis", 1)[0]
    else:
        text = text.split(r"\chapter{Trajectory Optimization}", 1)[1].split(
            r"\chapter{Funnel Synthesis}", 1
        )[0]
    for required in [
        r"\frac{dx}{ds}=T f",
        r"u_*\in\operatorname*{arg\,min}",
        r"6D^2/T^3",
        "Hermite--Simpson",
        "first passage",
        "multiplicative",
        "not a robustness certificate",
        "https://www.nature.com/articles/29528",
    ]:
        assert required in text
    for incorrect in ["massive positive", "5-millisecond", "must be maximized", "weaponizing"]:
        assert incorrect not in text
