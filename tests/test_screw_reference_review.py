"""Manufactured checks for the reference's geometry, load, and dynamics arguments.

These fixtures check declared algebra, not human biomechanics. The source contract
checks that the associated derivations are published; lead review checks meaning.
"""

from pathlib import Path

import numpy as np
import pytest

from src.affine_control.dynamics import skew
from src.tools.screw_examples import adjoint

ARTICLE = Path(__file__).resolve().parents[1] / "articles/screw-theory-reference.qmd"
ALGEBRA_ATOL = 1e-12  # Roundoff bound for the small, well-conditioned fixtures.


def test_reference_contains_the_reviewed_derivations() -> None:
    """Keep the published explanations attached to the checked failure modes."""
    source = ARTICLE.read_text(encoding="utf-8")
    labels = (
        "spatial-velocity",
        "pitch",
        "duality",
        "load-residual",
        "wrench-input",
        "forward-body",
        "constrained",
        "zvcf",
    )
    for label in labels:
        assert f"{{#eq-screw-{label}}}" in source


def test_nonzero_pitch_and_axis_gauge() -> None:
    """A pitch term survives changing the representative point on the axis."""
    omega = np.array([0.0, 0.0, 2.0])
    axis = np.array([1.0, 0.0, 0.0])
    pitch = 0.3
    velocity = -np.cross(omega, axis) + pitch * omega
    np.testing.assert_allclose(velocity, [0, -2, 0.6], atol=ALGEBRA_ATOL, rtol=0)
    norm_squared = float(omega @ omega)
    assert float(omega @ velocity) / norm_squared == pytest.approx(pitch, rel=0, abs=ALGEBRA_ATOL)
    np.testing.assert_allclose(
        np.cross(omega, velocity) / norm_squared, axis, atol=ALGEBRA_ATOL, rtol=0
    )
    shifted_axis = axis + 3.5 * omega
    np.testing.assert_allclose(
        -np.cross(omega, shifted_axis) + pitch * omega,
        velocity,
        atol=ALGEBRA_ATOL,
        rtol=0,
    )


def test_spatial_linear_component_is_not_body_origin_speed() -> None:
    """Rotation about a stationary displaced origin has nonzero spatial v."""
    omega = np.array([0.0, 0.0, 2.0])
    origin = np.array([1.0, 0.0, 0.0])
    spatial_linear = -np.cross(omega, origin)
    np.testing.assert_allclose(spatial_linear, [0, -2, 0], atol=ALGEBRA_ATOL, rtol=0)
    np.testing.assert_allclose(
        spatial_linear + np.cross(omega, origin), 0, atol=ALGEBRA_ATOL, rtol=0
    )


def test_current_jacobian_column_moves_with_upstream_joint() -> None:
    """The rotated second joint vanishes at its current axis, not its home axis."""
    home_screw = np.array([0.0, 0.0, 1.0, 0.0, -1.0, 0.0])
    transform = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    current = adjoint(transform) @ home_screw
    np.testing.assert_allclose(current, [0, 0, 1, 1, 0, 0], atol=ALGEBRA_ATOL, rtol=0)
    np.testing.assert_allclose(
        current[3:] + np.cross(current[:3], [0, 1, 0]), 0, atol=ALGEBRA_ATOL, rtol=0
    )
    assert np.linalg.norm(current[3:] + np.cross(current[:3], [1, 0, 0])) > 1


def test_incompatible_effort_has_a_nonzero_least_squares_residual() -> None:
    """Full column rank does not make a 7-by-6 load map surjective."""
    load_map = np.vstack([np.eye(6), np.eye(6)[0]])
    effort = np.array([1.0, 0, 0, 0, 0, 0, -1.0])
    wrench = np.linalg.lstsq(load_map, effort, rcond=None)[0]
    np.testing.assert_allclose(wrench, 0, atol=1e-14, rtol=0)
    assert np.linalg.norm(effort - load_map @ wrench) == pytest.approx(
        np.sqrt(2), rel=0, abs=ALGEBRA_ATOL
    )
    compatible_wrench = np.arange(1.0, 7.0)
    compatible_effort = load_map @ compatible_wrench
    recovered = np.linalg.lstsq(load_map, compatible_effort, rcond=None)[0]
    np.testing.assert_allclose(recovered, compatible_wrench, atol=ALGEBRA_ATOL, rtol=0)


def test_metric_must_follow_units_at_a_fixed_moment_origin() -> None:
    """Changing numerical moment units changes an unweighted minimizer."""
    constraint = np.array([0.001, 1.0])  # Moment in N mm; force in N; lever arm 1 m.
    unweighted = constraint * (2.0 / float(constraint @ constraint))
    physical = unweighted * np.array([1e-3, 1.0])
    expected = np.array([2e-6, 2.0]) / (1 + 1e-6)
    np.testing.assert_allclose(physical, expected, atol=ALGEBRA_ATOL, rtol=0)
    converted_metric = np.diag([1e-6, 1.0])
    direction = np.linalg.solve(converted_metric, constraint)
    weighted = direction * (2.0 / float(constraint @ direction))
    np.testing.assert_allclose(weighted, [1000, 1], atol=ALGEBRA_ATOL, rtol=0)
    np.testing.assert_allclose(weighted * [1e-3, 1], [1, 1], atol=ALGEBRA_ATOL, rtol=0)


def test_declared_coadjoint_sign_agrees_with_euler_equation() -> None:
    """A torque-free asymmetric body's spin changes with the stated sign."""
    inertia = np.diag([2.0, 3.0, 4.0])
    omega = np.array([1.0, 2.0, 3.0])
    acceleration = np.linalg.solve(inertia, -np.cross(omega, inertia @ omega))
    np.testing.assert_allclose(acceleration, [-3, 2, -0.5], atol=ALGEBRA_ATOL, rtol=0)
    spatial_inertia = np.diag([2.0, 3.0, 4.0, 5.0, 5.0, 5.0])
    twist = np.r_[omega, np.zeros(3)]
    ad_twist = np.block([[skew(omega), np.zeros((3, 3))], [np.zeros((3, 3)), skew(omega)]])
    ad_star = -ad_twist.T
    spatial_acceleration = np.linalg.solve(spatial_inertia, -ad_star @ spatial_inertia @ twist)
    np.testing.assert_allclose(
        spatial_acceleration, np.r_[acceleration, np.zeros(3)], atol=ALGEBRA_ATOL, rtol=0
    )


def test_constraint_reaction_depends_on_input_with_affine_acceleration() -> None:
    """An ideal fixed constraint changes its reaction without violating closure."""
    mass = np.diag([2.0, 3.0])
    constraint = np.array([[1.0, 1.0]])
    load = np.array([0.0, -3.0])
    actuation = np.array([1.0, 0.0])
    inputs = np.array([0.0, 2.5, 5.0])
    system = np.block([[mass, -constraint.T], [constraint, np.zeros((1, 1))]])
    right_hand_sides = np.vstack([load[:, None] + actuation[:, None] * inputs, np.zeros(3)])
    solutions = np.linalg.solve(system, right_hand_sides)
    np.testing.assert_allclose(solutions[:, 0], [0.6, -0.6, 1.2], atol=ALGEBRA_ATOL, rtol=0)
    np.testing.assert_allclose(solutions[:, 2], [1.6, -1.6, -1.8], atol=ALGEBRA_ATOL, rtol=0)
    np.testing.assert_allclose(
        solutions[:, 1], (solutions[:, 0] + solutions[:, 2]) / 2, atol=ALGEBRA_ATOL, rtol=0
    )
    np.testing.assert_allclose(constraint @ solutions[:2], 0, atol=ALGEBRA_ATOL, rtol=0)
