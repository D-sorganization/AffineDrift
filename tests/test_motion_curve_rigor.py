"""Independent examples for geometry, force, and transverse dynamics."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _curvature(velocity: np.ndarray, acceleration: np.ndarray) -> float:
    """Evaluate Euclidean curvature from the normal acceleration component."""
    speed = np.linalg.norm(velocity)
    tangent = velocity / speed
    normal_acceleration = acceleration - tangent * np.dot(tangent, acceleration)
    return float(np.linalg.norm(normal_acceleration) / speed**2)


def test_ellipse_curvature_is_largest_at_major_axis_endpoints() -> None:
    major, minor = 2.0, 1.0
    assert _curvature(np.array([0.0, minor]), np.array([-major, 0.0])) == 2.0
    assert _curvature(np.array([-major, 0.0]), np.array([0.0, -minor])) == 0.25


def test_zero_curvature_at_a_point_does_not_make_a_straight_segment() -> None:
    assert _curvature(np.array([1.0, 0.0]), np.array([0.0, 0.0])) == 0.0
    time = 0.1
    assert _curvature(np.array([1.0, 3 * time**2]), np.array([0.0, 6 * time])) > 0


def test_reparameterization_preserves_curvature_but_anisotropic_scaling_does_not() -> None:
    phase = 0.7
    velocity = np.array([-np.sin(phase), np.cos(phase)])
    acceleration = np.array([-np.cos(phase), -np.sin(phase)])
    rate, rate_derivative = 3.0, 0.8
    assert _curvature(
        rate * velocity, rate**2 * acceleration + rate_derivative * velocity
    ) == pytest.approx(1.0)
    scale = np.diag([2.0, 1.0])
    assert _curvature(scale @ velocity, scale @ acceleration) != pytest.approx(1.0)


def test_signed_helix_torsion_changes_under_reflection() -> None:
    radius = 2.0
    for pitch in [-1.0, 1.0]:
        velocity = np.array([0.0, radius, pitch])
        acceleration = np.array([-radius, 0.0, 0.0])
        jerk = np.array([0.0, -radius, 0.0])
        cross = np.cross(velocity, acceleration)
        torsion = np.dot(cross, jerk) / np.dot(cross, cross)
        assert torsion == pytest.approx(pitch / (radius**2 + pitch**2))


def test_circular_constraint_supplies_normal_force_with_zero_work() -> None:
    mass, radius, speed = 0.2, 1.0, 20.0
    position = np.array([radius, 0.0])
    velocity = np.array([0.0, speed])
    reaction = -(mass * speed**2 / radius**2) * position
    assert np.linalg.norm(reaction) == pytest.approx(80.0)
    assert np.dot(reaction, velocity) == 0.0


def test_task_acceleration_requires_jacobian_rate_term() -> None:
    angle, rate, acceleration, length = 0.4, 3.0, 0.7, 2.0
    jacobian = length * np.array([-np.sin(angle), np.cos(angle)])
    jacobian_rate = -length * rate * np.array([np.cos(angle), np.sin(angle)])
    task_acceleration = jacobian * acceleration + jacobian_rate * rate
    assert _curvature(jacobian * rate, task_acceleration) == pytest.approx(1 / length)
    assert _curvature(jacobian * rate, jacobian * acceleration) == pytest.approx(0.0, abs=1e-15)


def test_total_force_budget_couples_tangential_and_normal_acceleration() -> None:
    mass, force_limit, curvature, speed = 2.0, 10.0, 0.5, 3.0
    normal_acceleration = curvature * speed**2
    tangent_limit = np.sqrt((force_limit / mass) ** 2 - normal_acceleration**2)
    assert tangent_limit == pytest.approx(np.sqrt(4.75))
    assert mass * np.hypot(tangent_limit, normal_acceleration) == pytest.approx(force_limit)


def test_path_parameter_rate_differs_from_cartesian_speed() -> None:
    parameter, rate = 0.0, 2.0
    path_derivative = np.array([1.0, np.pi * np.cos(np.pi * parameter)])
    assert np.linalg.norm(path_derivative * rate) == pytest.approx(2 * np.sqrt(1 + np.pi**2))
    assert np.linalg.norm(path_derivative * rate) != rate


def test_same_circle_can_have_opposite_transverse_stability() -> None:
    radius, angular_rate, phase = 2.0, 1.3, 0.4
    radial = np.array([np.cos(phase), np.sin(phase)])
    tangent = np.array([-np.sin(phase), np.cos(phase)])
    epsilon = 1e-6
    for growth in [-0.7, 0.7]:

        def field(point: np.ndarray, radial_growth: float = growth) -> np.ndarray:
            """Return a circular flow with independently selected radial growth."""
            norm = np.linalg.norm(point)
            return radial_growth * (norm - radius) * point / norm + angular_rate * np.array(
                [-point[1], point[0]]
            )

        np.testing.assert_allclose(field(radius * radial), radius * angular_rate * tangent)
        derivative = (field((radius + epsilon) * radial) - field((radius - epsilon) * radial)) / (
            2 * epsilon
        )
        assert radial @ derivative == pytest.approx(growth)


def test_phase_denominator_and_normal_transport_match_circle_coordinates() -> None:
    radius, angular_rate, transverse_error = 2.0, 1.3, 0.2
    # Inward normal: x = (R - xi) e_r; arc length s = R theta.
    tangent_field = angular_rate * (radius - transverse_error)
    phase_rate = tangent_field / (1 - transverse_error / radius)
    assert phase_rate == pytest.approx(radius * angular_rate)


def test_commuting_inputs_can_trace_a_curved_path() -> None:
    phase = 0.7
    control = np.array([-np.sin(phase), np.cos(phase)])
    control_rate = np.array([-np.cos(phase), -np.sin(phase)])
    assert _curvature(control, control_rate) == pytest.approx(1.0)
    input_jacobians = np.zeros((2, 2, 2))
    bracket = input_jacobians[1] @ np.array([1.0, 0.0]) - input_jacobians[0] @ np.array([0.0, 1.0])
    np.testing.assert_array_equal(bracket, np.zeros(2))


def test_rotating_normal_frame_requires_speed_times_skew_transport() -> None:
    decay, phase_speed, frame_rate = 0.7, 2.0, 0.4
    phase, step = 0.3, 1e-6
    transverse = np.array([0.2, -0.5])

    def rotation(angle: float) -> np.ndarray:
        """Return the orientation of a normal basis along a straight path."""
        return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

    physical = rotation(frame_rate * phase) @ transverse
    forward = rotation(frame_rate * (phase + phase_speed * step)).T @ (
        np.exp(-decay * step) * physical
    )
    backward = rotation(frame_rate * (phase - phase_speed * step)).T @ (
        np.exp(decay * step) * physical
    )
    measured_rate = (forward - backward) / (2 * step)
    skew = frame_rate * np.array([[0.0, -1.0], [1.0, 0.0]])
    expected_rate = (-decay * np.eye(2) - phase_speed * skew) @ transverse
    np.testing.assert_allclose(measured_rate, expected_rate, atol=1e-9)


@pytest.mark.parametrize(
    "edition",
    [
        "articles/The_Geometry_of_Motion/Volume_II/chapters/ch02_curves_in_state_space.tex",
        "articles/motion-control/chapter2.tex",
        "articles/motion-control/Control_Is_Motion_Complete.tex",
        "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    ],
)
def test_curve_editions_exclude_invalid_force_and_stability_inference(edition: str) -> None:
    text = (ROOT / edition).read_text(encoding="utf-8")
    for phrase in [
        "The geometry of the trajectory creates the forces",
        "A trajectory with low curvature is inherently easier to stabilize",
        "highest at the ends of the minor axis",
        "highly curved trajectory requires",
    ]:
        assert phrase not in text
    assert r"\det[p',p'',p''']" in text
    assert r"q''\dot\lambda^2" in text
