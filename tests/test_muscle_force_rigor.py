"""Independent dimensional, limiting and work checks for the muscle chapter."""

from pathlib import Path

import numpy as np
import pytest

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"
EDITIONS = [
    BOOK / "chapters/ch17_muscle_force_generation.tex",
    BOOK / "quarto/ch17_muscle_force_generation.qmd",
]


def test_gaussian_has_no_finite_zero_or_flat_plateau() -> None:
    lengths = np.array([0.5, 0.8, 1.0, 1.2, 1.5])
    values = np.exp(-(((lengths - 1) / 0.5) ** 2))
    np.testing.assert_allclose(values, [np.exp(-1), np.exp(-0.16), 1, np.exp(-0.16), np.exp(-1)])
    assert np.all(values > 0)
    assert values[1] < values[2]


def test_unilateral_passive_force_is_zero_when_slack_and_normalized() -> None:
    lengths = np.array([0.8, 1.0, 1.2, 1.6])
    force = np.expm1(4 * np.maximum(lengths - 1, 0)) / np.expm1(4 * 0.6)
    assert np.all(force >= 0)
    np.testing.assert_allclose(force[[0, 1, 3]], [0, 0, 1])
    assert force[2] == pytest.approx(1 / (1 + np.exp(0.8) + np.exp(1.6)))


def test_local_fiber_speed_and_hill_force_have_compatible_units() -> None:
    fiber_length_m, fiber_lengths_per_second = 0.1, 10.0
    maximum_speed_m_s = fiber_length_m * fiber_lengths_per_second
    moment_arm_m, angular_speed_rad_s = 0.02, 8.75
    shortening_speed_m_s = moment_arm_m * angular_speed_rad_s
    w = shortening_speed_m_s / maximum_speed_m_s
    force_ratio = (1 - w) / (1 + w / 0.4)
    assert maximum_speed_m_s == 1
    assert w == pytest.approx(0.175)
    assert force_ratio == pytest.approx(0.5739130434782609)
    assert force_ratio != pytest.approx(1 - w)
    np.testing.assert_allclose(0.1 * np.array([2, 4]), [0.2, 0.4])


def test_eccentric_branch_has_the_declared_limit_and_matching_slope() -> None:
    k, limit = 0.4, 1.4
    c = (limit - 1) / (1 + 1 / k)
    w = -1e10
    assert 1 + (limit - 1) * (-w) / (c - w) == pytest.approx(limit)
    delta = 1e-6
    left_slope = ((1 + (limit - 1) * delta / (c + delta)) - 1) / -delta
    right_slope = ((1 - delta) / (1 + delta / k) - 1) / delta
    assert left_slope == pytest.approx(right_slope, rel=1e-5)


def test_hill_power_peak_matches_independent_grid_search() -> None:
    k = 0.4
    speed = np.linspace(0, 1, 100001)
    power = speed * (1 - speed) / (1 + speed / k)
    analytical = np.sqrt(k * k + k) - k
    assert speed[np.argmax(power)] == pytest.approx(analytical, abs=1e-5)
    assert np.max(power) == pytest.approx(0.12133481811616936)
    assert power[0] == power[-1] == 0


def test_moment_arm_virtual_work_and_multijoint_cancellation() -> None:
    # Differentiate a length function independently of the claimed moment arms.
    def length(q: np.ndarray) -> float:
        return float(0.3 - 0.02 * q[0] + 0.01 * q[1])

    q, delta = np.array([0.2, -0.3]), 1e-5
    gradient = np.array(
        [(length(q + delta * e) - length(q - delta * e)) / (2 * delta) for e in np.eye(2)]
    )
    moment_arms = -gradient
    np.testing.assert_allclose(moment_arms, [0.02, -0.01], atol=1e-11)
    for velocity in [np.array([10, 20]), np.array([10, 0])]:
        length_rate = gradient @ velocity
        tendon_force = 100
        torque = moment_arms * tendon_force
        assert torque @ velocity == pytest.approx(-tendon_force * length_rate)
    assert gradient @ np.array([10, 20]) == pytest.approx(0, abs=1e-9)


def test_fixed_height_pennation_conserves_power() -> None:
    fiber_length, height = 0.1, 0.06
    cosine = np.sqrt(fiber_length**2 - height**2) / fiber_length
    path_rate, tendon_rate = -0.1, 0.02
    fiber_rate = cosine * (path_rate - tendon_rate)
    fiber_force = 100
    tendon_force = fiber_force * cosine
    assert fiber_rate == pytest.approx(-0.096)
    assert tendon_force * path_rate == pytest.approx(
        fiber_force * fiber_rate + tendon_force * tendon_rate
    )


def test_tendon_energy_matches_work_quadrature_and_force_derivative() -> None:
    force_ref, slack_length, strain_ref, k = 100, 0.2, 0.04, 3

    def energy(strain: float) -> float:
        return float(
            force_ref
            * slack_length
            / np.expm1(k)
            * (strain_ref / k * np.expm1(k * strain / strain_ref) - strain)
        )

    extension = np.linspace(0, slack_length * strain_ref, 10001)
    force = force_ref * np.expm1(k * extension / (slack_length * strain_ref)) / np.expm1(k)
    work = np.sum((force[:-1] + force[1:]) / 2 * np.diff(extension))
    assert work == pytest.approx(energy(strain_ref), rel=2e-8)
    assert work == pytest.approx(0.22475010947366192, rel=2e-8)
    d_extension = 1e-8
    derivative = (
        energy(strain_ref + d_extension / slack_length)
        - energy(strain_ref - d_extension / slack_length)
    ) / (2 * d_extension)
    assert derivative == pytest.approx(force_ref, rel=1e-8)


def test_activation_time_constant_is_not_a_pure_delay() -> None:
    tau = 0.025
    assert 1 - np.exp(-tau / tau) == pytest.approx(0.6321205588)
    assert -tau * np.log(0.5) == pytest.approx(0.01732867951)
    assert -tau * np.log(0.05) == pytest.approx(0.07489330684)
    assert 1 - np.exp(-0.05 / tau) == pytest.approx(0.8646647168)
    assert 1 - (1 - 0.005 / tau) ** 13 < 0.95
    assert 1 - (1 - 0.005 / tau) ** 14 >= 0.95


def test_finite_horizon_response_matches_direct_time_integration() -> None:
    duration, tau, maximum_torque, inertia = 0.05, 0.025, 2, 0.1
    times = np.linspace(0, duration, 100001)
    acceleration = maximum_torque / inertia * (1 - np.exp(-times / tau))
    velocity = np.sum((acceleration[:-1] + acceleration[1:]) / 2 * np.diff(times))
    weighted_acceleration = (duration - times) * acceleration
    position = np.sum((weighted_acceleration[:-1] + weighted_acceleration[1:]) / 2 * np.diff(times))
    exact_velocity = maximum_torque / inertia * (duration - tau * (1 - np.exp(-duration / tau)))
    exact_position = (
        maximum_torque
        / inertia
        * (duration**2 / 2 - tau * duration + tau**2 * (1 - np.exp(-duration / tau)))
    )
    assert velocity == pytest.approx(exact_velocity, rel=1e-9)
    assert position == pytest.approx(exact_position, rel=1e-9)
    assert position == pytest.approx(0.010808308959542342)


def test_net_torque_does_not_identify_muscle_force() -> None:
    moment_arms = np.array([0.02, -0.02])
    forces = np.array([[100, 0], [200, 100]])
    np.testing.assert_allclose(forces @ moment_arms, [2, 2])
    np.testing.assert_allclose(np.sum(forces, axis=1), [100, 300])


@pytest.mark.parametrize("path", EDITIONS, ids=["print", "web"])
def test_chapter_removes_false_speed_evidence_and_preserves_technical_treatment(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for claim in [
        "why drift wins at impact",
        "sarcomeres contracting in parallel",
        "the chains break",
    ]:
        assert claim not in text
    for concept in [
        "virtual work",
        "fixed-height",
        "0.5739",
        "0.22475",
        "74.89",
        "finite-horizon",
        "worked answers",
        "ideal torque actuators",
        r"63.2\%",
        r"50\%",
        r"95\%",
    ]:
        assert concept in text
