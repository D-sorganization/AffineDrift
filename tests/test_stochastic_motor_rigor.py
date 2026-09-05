"""Independent analytic and numerical checks for motor-variability claims."""

from pathlib import Path

import numpy as np
import pytest
from numpy.polynomial.hermite import hermgauss
from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
GRAVITY_M_S2 = 9.81


def test_signal_dependent_standard_deviation_and_variance_scale_differently() -> None:
    coefficient = 0.15
    commands = np.array([2.0, 4.0])
    deviations = coefficient * commands
    assert deviations[1] / deviations[0] == 2
    assert deviations[1] ** 2 / deviations[0] ** 2 == 4


def test_brownian_increment_scaling_survives_mesh_refinement() -> None:
    duration, diffusion = 2.0, 0.3
    for steps in (10, 100, 1000):
        dt = duration / steps
        correct_variance = np.sum(np.full(steps, diffusion * np.sqrt(dt)) ** 2)
        incorrect_variance = np.sum(np.full(steps, diffusion * dt) ** 2)
        assert correct_variance == pytest.approx(diffusion**2 * duration)
        assert incorrect_variance == pytest.approx(correct_variance * dt)


def test_multiplicative_noise_mean_and_second_moment_by_gaussian_quadrature() -> None:
    nodes, weights = hermgauss(100)
    normal_nodes, normal_weights = np.sqrt(2) * nodes, weights / np.sqrt(np.pi)
    drift, diffusion, time = -1.0, 2.0, 1.0
    samples = np.exp((drift - diffusion**2 / 2) * time + diffusion * np.sqrt(time) * normal_nodes)
    mean = normal_weights @ samples
    second = normal_weights @ samples**2
    assert mean == pytest.approx(np.exp(-1), rel=1e-12)
    assert second == pytest.approx(np.exp(2), rel=1e-12)
    assert mean < 1 < second


def test_multiplicative_covariance_term_changes_the_answer() -> None:
    drift, multiplicative, additive, initial = -1.0, 0.5, 0.3, 0.1
    rate = 2 * drift + multiplicative**2
    full = solve_ivp(
        lambda _t, variance: rate * variance + additive**2,
        (0, 2),
        [initial],
        rtol=1e-11,
        atol=1e-13,
    )
    assert full.success
    exact = initial * np.exp(rate * 2) + additive**2 * np.expm1(rate * 2) / rate
    additive_only = initial * np.exp(2 * drift * 2) + additive**2 * np.expm1(2 * drift * 2) / (
        2 * drift
    )
    assert full.y[0, -1] == pytest.approx(exact, rel=1e-9)
    assert exact > additive_only


def test_lower_peak_can_have_higher_variance_at_equal_mean_displacement() -> None:
    early_mean = quad(lambda _t: 0.2, 0, 1)[0]
    late_mean = quad(lambda _t: 1, 1, 1.2)[0]
    early_variance = quad(lambda _t: (10 * 0.2) ** 2, 0, 1)[0]
    late_variance = quad(lambda _t: 1, 1, 1.2)[0]
    assert early_mean == pytest.approx(late_mean)
    assert early_variance == pytest.approx(4)
    assert late_variance == pytest.approx(0.2)
    assert early_variance / late_variance == pytest.approx(20)


def test_mechanical_transport_determines_task_covariance() -> None:
    # White acceleration noise in a double integrator; position variance T^3/3.
    duration, diffusion = 2.0, 0.3
    matrix = np.array([[0.0, 1.0], [0.0, 0.0]])
    forcing = np.diag([0.0, diffusion**2])

    def dynamics(_time: float, flat: np.ndarray) -> np.ndarray:
        covariance = flat.reshape(2, 2)
        return (matrix @ covariance + covariance @ matrix.T + forcing).ravel()

    result = solve_ivp(dynamics, (0, duration), np.zeros(4), rtol=1e-11, atol=1e-13)
    assert result.success
    covariance = result.y[:, -1].reshape(2, 2)
    sensitivity_integral = quad(lambda t: (diffusion * (duration - t)) ** 2, 0, duration)[0]
    assert covariance[0, 0] == pytest.approx(sensitivity_integral)
    assert covariance[0, 0] == pytest.approx(diffusion**2 * duration**3 / 3)
    assert covariance[0, 1] == pytest.approx(diffusion**2 * duration**2 / 2)


def test_minimum_jerk_quintic_boundary_conditions_and_cost() -> None:
    distance, duration = 1.7, 2.3
    polynomial = np.polynomial.Polynomial([0, 0, 0, 10, -15, 6])
    for order in (1, 2):
        assert polynomial.deriv(order)([0, 1]) == pytest.approx([0, 0])
    assert polynomial([0, 1]) == pytest.approx([0, 1])
    assert polynomial.deriv(6).coef == pytest.approx([0])
    cost = quad(
        lambda t: (distance / duration**3 * polynomial.deriv(3)(t / duration)) ** 2, 0, duration
    )[0]
    assert cost == pytest.approx(720 * distance**2 / duration**5)


def test_zero_kinematic_jerk_does_not_imply_zero_torque() -> None:
    mass, length, angle = 4.0, 0.5, np.pi / 2
    holding_torque = mass * GRAVITY_M_S2 * length * np.sin(angle)
    constant_angle = np.polynomial.Polynomial([angle])
    assert constant_angle.deriv(3)(1) == 0
    assert holding_torque == pytest.approx(19.62)


@pytest.mark.parametrize(("risk_weight", "optimum"), [(0.1, 1.0), (1.0, 0.5)])
def test_signal_dependent_noise_can_select_saturated_or_interior_effort(
    risk_weight: float, optimum: float
) -> None:
    result = minimize_scalar(
        lambda control: -(control - risk_weight * control**2),
        bounds=(0, 1),
        method="bounded",
        options={"xatol": 1e-12},
    )
    assert result.success
    assert result.x == pytest.approx(optimum, abs=1e-6)


def test_fixed_mean_displacement_duration_changes_variance() -> None:
    distance, diffusion = 1.5, 0.2
    variances = []
    for duration in (1.0, 2.0):
        control = distance / duration
        assert control * duration == distance
        variances.append(quad(lambda _t, held=control: (diffusion * held) ** 2, 0, duration)[0])
    assert variances[1] == pytest.approx(variances[0] / 2)


def test_quadratic_loss_keeps_bias_and_covariance() -> None:
    outcomes = np.array([[1.0, 2.0], [2.0, 0.0], [-1.0, 3.0]])
    probabilities = np.array([0.2, 0.5, 0.3])
    weight = np.diag([2.0, 0.5])
    mean = probabilities @ outcomes
    centered = outcomes - mean
    covariance = centered.T @ (probabilities[:, None] * centered)
    expected_loss = sum(
        p * (outcome @ weight @ outcome) for p, outcome in zip(probabilities, outcomes, strict=True)
    )
    assert expected_loss == pytest.approx(mean @ weight @ mean + np.trace(weight @ covariance))
    assert expected_loss > np.trace(weight @ covariance)


def test_risk_sensitive_cost_expansion_for_a_bounded_distribution() -> None:
    theta, probability = 1e-4, 0.25
    mean = 2 * probability
    variance = 4 * probability - mean**2
    exact = np.log1p(probability * np.expm1(2 * theta)) / theta
    approximation = mean + theta * variance / 2
    assert exact == pytest.approx(approximation, abs=2e-9)
    assert exact > mean


def test_positive_gaussian_tail_is_not_a_bounded_disturbance_guarantee() -> None:
    failure_probability = 2 * norm.sf(4)
    assert 0 < failure_probability < 0.0001
    assert (1 - failure_probability) ** 10 < 1 - failure_probability


def test_ito_phase_chain_rule_requires_second_derivative() -> None:
    nodes, weights = hermgauss(20)
    time, diffusion = 0.7, 0.4
    states = diffusion * np.sqrt(2 * time) * nodes
    expected_squared_phase = (weights @ states**2) / np.sqrt(np.pi)
    assert expected_squared_phase == pytest.approx(diffusion**2 * time)
    assert expected_squared_phase > 0


def test_stratonovich_conversion_preserves_log_coordinate_drift() -> None:
    stratonovich_drift, diffusion = -1.0, 2.0
    ito_drift = stratonovich_drift + diffusion**2 / 2
    log_drift = ito_drift - diffusion**2 / 2
    assert log_drift == stratonovich_drift
    assert ito_drift > 0 > stratonovich_drift


@pytest.mark.parametrize(
    "source",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch09_stochastic_trajectories_motor_.tex",
        "articles/motion-control/chapter9.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_all_editions_distinguish_noise_evidence_objectives_and_guarantees(source: str) -> None:
    text = (ROOT / source).read_text(encoding="utf-8")
    if source.endswith(".qmd"):
        text = text.split("## Stochastic Trajectories", 1)[1].split("## Learning to Move", 1)[0]
    else:
        text = text.split(r"\chapter{Stochastic Trajectories", 1)[1].split(
            r"\chapter{Learning to Move}", 1
        )[0]
    for required in [
        r"\sqrt{\Delta t}",
        "mean-square stability",
        "twenty times",
        "post-movement interval",
        "One optimum saturates",
        "unbounded support",
        "random first-hit time",
        r"+\nabla\phi^\top G\,dW",
        "https://wolpertlab.neuroscience.columbia.edu/sites/default/files/content/papers/JonHamWol02.pdf",
    ]:
        assert required in text
    for incorrect in [
        "crumbles deterministic",
        "maximum chaotic noise",
        "mathematically proven to be a sub-maximal",
        "only way to minimize",
        "entropy-like term",
        "AgrachevSachkov2004",
    ]:
        assert incorrect not in text
