"""Independent counterexamples for the Physics textbook's loop-mechanics claims."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "articles" / "The_Physics_of_Golf"


def test_platform_mobility_counts_include_leg_bodies_and_joints() -> None:
    """UPS telescoping legs give six freedoms; fixed SPS legs retain only spins."""
    ups_mobility = 6 * (14 - 1 - 18) + 6 * (2 + 1 + 3)
    fixed_sps_mobility = 6 * (8 - 1 - 12) + 12 * 3
    assert ups_mobility == 6
    assert fixed_sps_mobility - 6 == 0  # Six unobserved axial rod rotations.


def test_six_fixed_lengths_can_fix_platform_pose() -> None:
    """Generic length gradients remove platform motion despite each rod's axial spin."""
    rng = np.random.default_rng(9)  # Reproducible, nonsymmetric anchor geometry.
    base = np.column_stack((rng.uniform(-2, 2, (6, 2)), np.zeros(6)))
    platform = np.column_stack((rng.uniform(-1, 1, (6, 2)), np.zeros(6)))
    legs = platform + [0.0, 0.0, 1.0] - base
    directions = legs / np.linalg.norm(legs, axis=1, keepdims=True)
    length_jacobian = np.column_stack((np.cross(platform, directions), directions))
    assert np.linalg.matrix_rank(length_jacobian) == 6


def test_two_arm_closure_preserves_common_hand_motion() -> None:
    """Constraint-null velocities move both endpoints; they need not fix the task."""
    left = np.array([[-1.0, -1.0], [1.0, 0.0]])
    right = np.array([[-1.0, -1.0], [-1.0, 0.0]])
    closure = np.column_stack((left, -right))
    velocity = np.array([1.0, -1.0, -1.0, 1.0])
    assert np.linalg.matrix_rank(closure) == 2
    np.testing.assert_allclose(closure @ velocity, 0.0)
    np.testing.assert_allclose(left @ velocity[:2], [0.0, 1.0])
    np.testing.assert_allclose(right @ velocity[2:], [0.0, 1.0])


def test_applied_load_changes_reaction_without_changing_motion() -> None:
    """Kinematic compatibility does not determine an unknown actuator/reaction split."""
    mass = np.diag([2.0, 1.0])
    closure = np.array([[1.0, -1.0]])
    system = np.block([[mass, -closure.T], [closure, np.zeros((1, 1))]])
    first = np.linalg.solve(system, [1.0, 0.0, 0.0])
    second = np.linalg.solve(system, [2.0, -1.0, 0.0])
    np.testing.assert_allclose(first, [1 / 3, 1 / 3, -1 / 3])
    np.testing.assert_allclose(second, [1 / 3, 1 / 3, -4 / 3])


def test_radial_load_has_no_moment_about_its_rotation_center() -> None:
    """A large load magnitude is neither a moment arm nor an energy source."""
    radius = np.array([0.6, 0.0, 0.0])
    angular_velocity = np.array([0.0, 0.0, 15.0])
    force = -3.0 * np.cross(angular_velocity, np.cross(angular_velocity, radius))
    np.testing.assert_allclose(force, [405.0, 0.0, 0.0])
    np.testing.assert_allclose(np.cross(radius, force), 0.0)
    assert force @ np.cross(angular_velocity, radius) == 0.0


def test_cop_and_free_moment_reconstruct_measured_wrench() -> None:
    """Right-handed force-on-golfer convention fixes both COP signs and yaw offset."""
    force = np.array([20.0, 30.0, 800.0])
    point = np.array([0.2, -0.1, 0.0])
    moment = np.cross(point, force) + [0.0, 0.0, 5.0]
    cop = np.array([-moment[1] / force[2], moment[0] / force[2], 0.0])
    free_moment = moment[2] - np.cross(cop, force)[2]
    np.testing.assert_allclose(cop, point)
    assert free_moment == pytest.approx(5.0)


def test_two_point_contacts_have_one_internal_force_direction() -> None:
    """Only a line-directed opposing pair cancels its moment as well as its force."""
    offset = np.array([0.2, 0.0, 0.0])
    cross = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -0.2], [0.0, 0.2, 0.0]])
    grasp = np.block([[np.zeros((3, 3)), cross], [np.eye(3), np.eye(3)]])
    assert np.linalg.matrix_rank(grasp) == 5
    np.testing.assert_allclose(grasp @ np.concatenate((offset, -offset)), 0.0)
    transverse_pair = np.array([0.0, 1.0, 0.0, 0.0, -1.0, 0.0])
    assert np.linalg.norm(grasp @ transverse_pair) == pytest.approx(0.2)


@pytest.mark.parametrize(
    "relative_path",
    ["chapters/ch09_parallel_mechanisms.tex", "quarto/ch09_parallel_mechanisms.qmd"],
)
def test_paired_chapters_exclude_disproved_explanations(relative_path: str) -> None:
    """Keep the worked mathematics and the accessible interpretation consistent."""
    text = (BOOK / relative_path).read_text(encoding="utf-8")
    for phrase in (
        "The loop constraint is what creates the X-factor",
        "The only reason it",
        "ground does mechanical work on the golfer",
        "drift forces exceed active muscle torques by a factor of 5",
        "Uniquely determined:} Constraint forces",
        "Uniquely determined:** constraint forces",
        "shortening eccentrically",
    ):
        assert phrase not in text
