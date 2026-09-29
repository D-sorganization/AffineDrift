"""Independent synthetic checks for the green-simulation article's model boundaries."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

ARTICLE = Path(__file__).resolve().parents[1] / "articles/green-simulation.qmd"


@pytest.mark.parametrize("surface_speed", [0.0, 3.0])
def test_signed_slip_reaches_common_speed_and_dissipates_energy(surface_speed: float) -> None:
    speed, alpha, friction_accel = 2.0, 0.4, 3.0
    slip = speed - surface_speed
    duration = abs(slip) / (friction_accel * (1 + 1 / alpha))
    direction = math.copysign(1, slip)
    final_speed = speed - friction_accel * direction * duration
    final_surface_speed = surface_speed + friction_accel / alpha * direction * duration
    assert final_speed == pytest.approx(final_surface_speed)
    assert final_speed == pytest.approx((speed + alpha * surface_speed) / (1 + alpha))
    assert (1 + alpha) * final_speed**2 <= speed**2 + alpha * surface_speed**2
    assert (final_speed > speed) == (slip < 0)


def test_incline_acceleration_satisfies_rolling_energy_balance() -> None:
    mass, alpha, gravity, beta, speed, a0 = 0.046, 0.4, 9.80665, 0.05, 1.2, 0.46
    accel = gravity * math.sin(beta) / (1 + alpha) - a0 * math.cos(beta)
    power_gravity = mass * gravity * math.sin(beta) * speed
    power_loss = mass * (1 + alpha) * a0 * math.cos(beta) * speed
    assert mass * (1 + alpha) * speed * accel == pytest.approx(power_gravity - power_loss)


def test_five_percent_is_not_downhill_acceleration_at_stimp_twelve() -> None:
    gravity, alpha, a0, grade = 9.80665, 0.4, 5.49 / 12, 0.05
    beta = math.atan(grade)
    assert a0 / gravity < grade < (1 + alpha) * a0 / gravity
    assert gravity * math.sin(beta) / (1 + alpha) - a0 * math.cos(beta) < 0


def test_nonnegative_slip_and_disc_events_can_miss_zeroes() -> None:
    # Tangential norm zero and two disc-boundary crossings both evade endpoint signs.
    assert abs(-1.0) * abs(1.0) > 0
    assert abs(0.0) == 0
    radius = 0.054
    assert ((-0.06) ** 2 - radius**2) * (0.065**2 - radius**2) > 0
    assert 0.0**2 - radius**2 < 0


def test_early_velocity_impulse_has_more_remaining_time() -> None:
    early = 0.05 * (4.0 - 0.5)
    late = 0.05 * (4.0 - 3.9)
    assert early == pytest.approx(0.175)
    assert late == pytest.approx(0.005)
    assert early / late == pytest.approx(35.0)


def test_zero_mean_noise_can_help_a_nominal_miss() -> None:
    nominal = 1.5
    perturbations = np.array([-1.0, 1.0])
    assert perturbations.mean() == 0.0
    assert not abs(nominal) <= 1.0
    assert np.mean(abs(nominal + perturbations) <= 1.0) == 0.5


def test_dissipative_tensor_can_produce_transverse_acceleration() -> None:
    resistance = np.array([[2.0, 1.0], [1.0, 2.0]])
    velocity = np.array([1.0, 0.0])
    acceleration = -resistance @ velocity
    assert np.linalg.eigvalsh(resistance) == pytest.approx([1.0, 3.0])
    assert acceleration == pytest.approx([-2.0, -1.0])
    assert velocity @ acceleration < 0


def test_continuous_grid_height_does_not_guarantee_continuous_slope() -> None:
    heights = np.array([0.0, 0.01, 0.03])
    spacing = 0.1
    slopes = np.diff(heights) / spacing
    assert slopes == pytest.approx([0.1, 0.2])
    assert heights[0] + spacing * slopes[0] == pytest.approx(heights[1])
    assert heights[2] - spacing * slopes[1] == pytest.approx(heights[1])


def test_monte_carlo_error_and_aim_area_have_declared_meanings() -> None:
    assert math.sqrt(0.5 * 0.5 / 1000) == pytest.approx(0.0158113883)
    area_radians = math.radians(2.0) * 0.2
    area_degrees = 2.0 * 0.2
    assert area_degrees / area_radians == pytest.approx(180 / math.pi)


@pytest.mark.parametrize(
    "required",
    [
        r"\frac{\mathbf g_\parallel}{1+\alpha}",
        "not a universal probability ceiling",
        "35 times",
        "fixed 2 ms",
        "96ab281ef0af185640e93571dd4bf2b94ff761a5",
        "af7f2682213f57bb2e95052fed6d5b0740596cbd",
    ],
)
def test_article_preserves_corrected_model_and_version_boundaries(required: str) -> None:
    assert required in ARTICLE.read_text(encoding="utf-8")
