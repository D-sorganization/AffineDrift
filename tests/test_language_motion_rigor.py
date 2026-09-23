"""Check Chapter 2's published examples and concrete modeling regressions."""

import importlib
import re
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
EDITIONS = ("chapters/ch02_language_of_motion.tex", "quarto/ch02_language_of_motion.qmd")


@pytest.mark.parametrize("edition", EDITIONS)
@pytest.mark.parametrize(
    "unsupported",
    (
        "full 3D position of every point",
        "pointing vertically downward",
        "elbow angle from horizontal",
        "constraint forces are not muscle forces",
        "This is why the two joints are coupled",
        "both velocities are (nearly) zero",
        "given the trajectory, we can work backward to infer the forces",
    ),
)
def test_paired_sources_remove_identified_false_claims(edition, unsupported):
    source = (BOOK / edition).read_text(encoding="utf-8")
    assert unsupported not in source


def test_published_trajectory_has_signed_derivatives_and_declared_units():
    source = (BOOK / EDITIONS[1]).read_text(encoding="utf-8")
    example = re.search(r"```python\n# Manufactured Chapter 2 trajectory\n(.*?)```", source, re.S)
    assert example is not None, "Publish the reproducible trajectory replacing the old phase table"
    namespace = {}
    exec(compile(example.group(1), "chapter2-published-example", "exec"), namespace)
    np.testing.assert_allclose(namespace["q_deg"], [[90, -45], [67.5, -22.5], [0, 0]])
    np.testing.assert_allclose(namespace["rate_deg_s"], [[0, 90], [-180, 90], [-360, 90]])
    np.testing.assert_allclose(namespace["q_rad"], np.deg2rad(namespace["q_deg"]))
    np.testing.assert_allclose(namespace["rate_rad_s"], np.deg2rad(namespace["rate_deg_s"]))
    # Independently differentiate each coordinate's quadratic interpolant in time.
    for coordinate in range(2):
        polynomial = np.polyfit(namespace["time_s"], namespace["q_deg"][:, coordinate], 2)
        derivative = np.polyval(np.polyder(polynomial), namespace["time_s"])
        np.testing.assert_allclose(derivative, namespace["rate_deg_s"][:, coordinate], atol=1e-10)


@pytest.fixture
def model():
    return importlib.import_module(
        "docs.development.technical-review.build_double_pendulum_figures"
    )


def test_worked_downward_state_has_leftward_velocity_and_upward_curvature(model):
    q = np.zeros(2)
    rates = np.deg2rad([-360, 90])
    acceleration = np.deg2rad([-720, 0])
    velocity = model.endpoint_jacobian(q) @ rates
    np.testing.assert_allclose(velocity, [-2.2 * np.pi, 0], atol=1e-12)
    np.testing.assert_allclose(
        model.endpoint_acceleration(q, rates, acceleration),
        [-5.4 * np.pi, 3.65 * np.pi**2],
        atol=1e-12,
    )


def test_an_angle_turning_point_does_not_stop_the_endpoint(model):
    q, rates = np.deg2rad([90, -45]), np.deg2rad([0, 90])
    assert rates[0] == 0
    assert np.linalg.norm(model.endpoint_jacobian(q) @ rates) == pytest.approx(np.pi / 2)


def test_joint_rate_cancellation_depends_on_direction_and_configuration(model):
    jacobian = model.endpoint_jacobian(np.zeros(2))
    np.testing.assert_allclose(jacobian @ [1, -1.35], [0, 0], atol=1e-12)
    assert np.linalg.norm(jacobian @ [1, 1.35]) == pytest.approx(2.7)


def test_rolling_sphere_has_two_velocity_constraints_not_two_configuration_coordinates():
    # Velocity coordinates are (vx, vy, wx, wy, wz); center height is fixed.
    radius = 0.021
    constraint = np.array([[1, 0, 0, -radius, 0], [0, 1, radius, 0, 0]])
    angular_velocity = np.array([2.0, -3.0, 4.0])
    center_velocity = np.array([radius * angular_velocity[1], -radius * angular_velocity[0], 0])
    contact_velocity = center_velocity + np.cross(angular_velocity, [0, 0, -radius])
    np.testing.assert_allclose(contact_velocity, 0, atol=1e-12)
    assert constraint.shape[1] - np.linalg.matrix_rank(constraint) == 3
    np.testing.assert_allclose(constraint @ np.r_[center_velocity[:2], angular_velocity], 0)


def test_phase_projection_hides_distinct_complete_states(model):
    rates = np.array([1.0, 0.0])
    first = model.endpoint_jacobian(np.array([0.0, 0.0])) @ rates
    second = model.endpoint_jacobian(np.array([0.0, np.pi / 2])) @ rates
    assert not np.allclose(first, second)


def test_translating_pivot_velocity_must_be_added(model):
    q, rates = np.array([0.3, -0.8]), np.array([1.0, -2.0])
    pivot_velocity = np.array([0.4, -0.2])
    step = 1e-6
    displacement = (step * pivot_velocity + model.endpoint(q + step * rates)) - (
        -step * pivot_velocity + model.endpoint(q - step * rates)
    )
    np.testing.assert_allclose(
        displacement / (2 * step), pivot_velocity + model.endpoint_jacobian(q) @ rates, atol=1e-9
    )
