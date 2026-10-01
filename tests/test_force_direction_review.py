"""Independent reference-point and inference checks for companion Chapter 9."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/proximal_distal_companion/chapters/ch09_force_direction.qmd"


def test_hand_force_moment_declares_application_point_and_center_of_mass() -> None:
    """The former L F_t moment about the force's own application point is incorrect."""
    source = CHAPTER.read_text(encoding="utf-8")
    assert "moment about the hand is approximately" not in source
    assert "center of mass" in source
    assert "zero moment about" in source


def test_power_invariance_and_geometric_controls_have_physical_conditions() -> None:
    """Coordinate invariance is not observer invariance or a feasible intervention."""
    source = CHAPTER.read_text(encoding="utf-8")
    assert "frame-invariant power" not in source
    assert "same observer" in source
    assert "bounded" in source
    assert "intrinsic" in source


def test_grip_force_has_zero_hand_moment_but_nonzero_center_moment() -> None:
    """A force at H cannot have an L F_t lever arm about H itself."""
    hand = np.zeros(3)
    center = np.array([0.6, 0.0, 0.0])
    force = np.array([80.0, 25.0, 0.0])
    np.testing.assert_allclose(np.cross(hand - hand, force), np.zeros(3))
    np.testing.assert_allclose(np.cross(hand - center, force), [0.0, 0.0, -15.0])
    # The same axial component can transfer power through a moving hand.
    assert force @ np.array([2.0, 0.0, 0.0]) == pytest.approx(160.0)


def test_coupled_mass_matrix_can_reverse_an_acceleration_component() -> None:
    """Positive drive in one coordinate induces opposite acceleration in another."""
    mass = np.array([[2.0, 1.0], [1.0, 2.0]])
    drive = np.array([1.0, 0.0])
    acceleration = np.linalg.solve(mass, drive)
    np.testing.assert_allclose(acceleration, [2.0 / 3.0, -1.0 / 3.0])
    assert np.linalg.eigvalsh(mass).min() > 0.0


def test_nonlinear_coordinate_change_introduces_velocity_bias() -> None:
    """The free Cartesian particle x=q^2 has nonzero bias in the nonlinear q chart."""
    coordinate, rate = 2.0, 0.3
    mass = 4.0 * coordinate**2
    bias = 4.0 * coordinate * rate**2
    acceleration = -bias / mass
    cartesian_acceleration = 2.0 * rate**2 + 2.0 * coordinate * acceleration
    assert bias != 0.0
    assert cartesian_acceleration == pytest.approx(0.0, abs=1e-15)
    # The zero Cartesian bias cannot map as an independent generalized-force vector.
    assert bias != (2.0 * coordinate) * 0.0


def test_reversing_separation_reverses_force_couple_only() -> None:
    """Retain the common-force moment and intrinsic contact moments."""
    midpoint = np.array([0.5, 0.1, 0.0])
    separation = np.array([0.2, 0.0, 0.0])
    resultant = np.array([10.0, 1.0, 2.0])
    differential = np.array([0.0, 15.0, 0.0])
    intrinsic = np.array([0.0, 0.0, 2.0])
    force_one, force_two = resultant / 2 + differential, resultant / 2 - differential
    moment = (
        np.cross(midpoint + separation / 2, force_one)
        + np.cross(midpoint - separation / 2, force_two)
        + intrinsic
    )
    common = np.cross(midpoint, resultant) + intrinsic
    couple = np.cross(separation, differential)
    np.testing.assert_allclose(moment, common + couple)
    swapped = (
        np.cross(midpoint - separation / 2, force_one)
        + np.cross(midpoint + separation / 2, force_two)
        + intrinsic
    )
    np.testing.assert_allclose(swapped, common - couple)
    assert not np.allclose(swapped, -moment)
    assert common[2] == pytest.approx(1.5)  # Survives collapsed hand separation.


def test_couple_collapse_needs_bounded_forces() -> None:
    """A shrinking separation need not reduce a couple if its force diverges."""
    epsilon = 1e-5
    separation = np.array([0.2, 0.0, 0.0])
    differential = np.array([0.0, 15.0, 0.0])
    initial = np.cross(separation, differential)
    np.testing.assert_allclose(np.cross(epsilon * separation, differential), epsilon * initial)
    np.testing.assert_allclose(np.cross(epsilon * separation, differential / epsilon), initial)


def test_power_changes_under_observer_translation() -> None:
    """A common axis rotation preserves a dot product; a new velocity observer need not."""
    force = np.array([3.0, 4.0, 0.0])
    velocity = np.array([2.0, 1.0, 0.0])
    observer_velocity = np.array([5.0, 0.0, 0.0])
    original = force @ velocity
    shifted = force @ (velocity - observer_velocity)
    assert original == pytest.approx(10.0)
    assert shifted == pytest.approx(-5.0)
    assert shifted - original == pytest.approx(-force @ observer_velocity)


def test_small_frame_error_can_reverse_a_small_transverse_component() -> None:
    """One degree of axial leakage can overwhelm a one-newton transverse signal."""
    error = np.deg2rad(1.0)
    axial, transverse = 100.0, 1.0
    measured_transverse = transverse * np.cos(error) - axial * np.sin(error)
    assert transverse > 0.0
    assert measured_transverse == pytest.approx(-0.74539, abs=1e-5)
    assert measured_transverse < 0.0
