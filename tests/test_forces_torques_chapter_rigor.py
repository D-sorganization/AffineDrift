"""Independent physical balances for Chapter 4 force and torque attribution."""

from importlib import import_module
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest


@pytest.fixture
def model() -> ModuleType:
    return import_module("docs.development.technical-review.build_forces_torques_figures")


@pytest.mark.parametrize("q", [[0, 0], [0, -0.1], [0.8, 0.7], [2.5, -1.2]])
def test_newton_euler_loads_recover_lagrange_torques(model: ModuleType, q: list) -> None:
    angles, rates, acceleration = np.asarray(q), np.array([2.1, -1.6]), np.array([3.2, -4.1])
    physical = model.body_loads(angles, rates, acceleration)
    mass, bias, gradient = model.DP.AFFINE.operators(angles, rates)
    np.testing.assert_allclose(physical["torque"], mass @ acceleration + bias + gradient)
    np.testing.assert_allclose(
        physical["base_force"] + 2.9 * model.GRAVITY_VECTOR,
        2.5 * physical["com_acceleration"][0] + 0.4 * physical["com_acceleration"][1],
    )


def test_physical_body_power_equals_independent_energy_derivative(model: ModuleType) -> None:
    q, rates, acceleration = np.array([0.6, -0.8]), np.array([1.7, -2.1]), np.array([3.0, -4.0])
    result = model.body_loads(q, rates, acceleration)
    step = 1e-6
    segments = import_module("docs.development.technical-review.build_constraint_forces_figures")
    derivative = (
        segments.segment_kinetic(q + step * rates, rates + step * acceleration)
        - segments.segment_kinetic(q - step * rates, rates - step * acceleration)
    ) / (2 * step)
    np.testing.assert_allclose(result["body_power"], derivative, atol=1e-9)
    assert sum(result["interface_force_power"]) == pytest.approx(0.0, abs=1e-12)


def test_endpoint_attribution_includes_curvature(model: ModuleType) -> None:
    q, rates, torque = np.array([0.5, -0.6]), np.array([3.0, -2.0]), np.array([5.0, 1.0])
    parts = model.acceleration_attribution(q, rates, torque)
    mass, bias, gravity = model.DP.AFFINE.operators(q, rates)
    acceleration = np.linalg.solve(mass, torque - bias - gravity)
    actual = model.DP.endpoint_acceleration(q, rates, acceleration)
    np.testing.assert_allclose(sum(parts.values()), actual)
    assert np.linalg.norm(parts["curvature"]) > 1


def test_rotating_transport_matches_position_second_derivative(model: ModuleType) -> None:
    state = model.RotatingState(
        relative_position=np.array([0.8, -0.3]),
        relative_velocity=np.array([0.4, 0.7]),
        relative_acceleration=np.array([-0.2, 0.1]),
        angular_rate=1.8,
        angular_acceleration=-0.6,
        origin_acceleration=np.array([0.3, -0.4]),
    )

    def position(time: float) -> np.ndarray:
        angle = state.angular_rate * time + 0.5 * state.angular_acceleration * time**2
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        relative = state.relative_position + time * state.relative_velocity
        relative += 0.5 * time**2 * state.relative_acceleration
        return 0.5 * time**2 * state.origin_acceleration + rotation @ relative

    step = 1e-4
    numerical = (position(step) - 2 * position(0) + position(-step)) / step**2
    np.testing.assert_allclose(model.transport_acceleration(state), numerical, atol=1e-7)


def test_wrench_shift_preserves_power_and_changes_moment(model: ModuleType) -> None:
    force = np.array([4.0, -3.0, 2.0])
    moment = np.array([1.0, 2.0, -1.0])
    offset = np.array([0.2, -0.4, 0.1])
    angular_rate = np.array([0.6, -0.7, 0.3])
    velocity = np.array([2.0, -1.0, 3.0])
    shifted = model.shift_moment(moment, force, offset)
    shifted_velocity = velocity + np.cross(angular_rate, offset)
    assert force @ velocity + moment @ angular_rate == pytest.approx(
        force @ shifted_velocity + shifted @ angular_rate
    )
    assert not np.allclose(shifted, moment)


def test_velocity_bias_scaling_does_not_establish_helpful_power(model: ModuleType) -> None:
    q, rates = np.array([0.0, -0.2]), np.array([2.0, 3.0])
    baseline = model.DP.AFFINE.operators(q, rates)[1]
    faster = model.DP.AFFINE.operators(q, 3 * rates)[1]
    reverse = model.DP.AFFINE.operators(q, -rates)[1]
    np.testing.assert_allclose(faster, 9 * baseline)
    np.testing.assert_allclose(reverse, baseline)
    forward_power, reversed_power = -baseline @ rates, -reverse @ (-rates)
    assert abs(forward_power) > 0
    assert forward_power == pytest.approx(-reversed_power)


@pytest.mark.parametrize(
    "edition", ["chapters/ch04_forces_and_torques.tex", "quarto/ch04_forces_and_torques.qmd"]
)
def test_paired_chapter_removes_unsupported_force_inference(edition: str) -> None:
    text = (Path(__file__).parents[1] / "articles/The_Physics_of_Golf" / edition).read_text(
        encoding="utf-8"
    )
    for required in ("whole-club COM", "negative torque", "moving origin", "not a measured golfer"):
        assert required in text
    for unsupported in (
        "Physics decides it",
        "free source of energy",
        "Elite golfers ride the passive dynamics",
        "all that work is already done",
        "M_{11} = 2.22",
        "M_{11} = 1.54",
    ):
        assert unsupported not in text


def test_web_math_uses_quarto_delimiters() -> None:
    """Avoid silently losing TeX commands in ordinary Markdown prose."""
    text = (
        Path(__file__).parents[1]
        / "articles/The_Physics_of_Golf/quarto/ch04_forces_and_torques.qmd"
    ).read_text(encoding="utf-8")
    assert r"\(" not in text
    assert r"\)" not in text
    assert r"$q_1=\theta_1$" in text
