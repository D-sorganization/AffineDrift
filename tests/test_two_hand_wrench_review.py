"""Independent mechanics and source boundaries for companion Chapter 12."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "articles/proximal_distal_companion/chapters/ch12_two_hands_one_wrench.qmd"


def _cross_matrix(vector: np.ndarray) -> np.ndarray:
    """Construct the linear cross-product operator from basis-vector images."""
    return np.column_stack([np.cross(vector, basis) for basis in np.eye(3)])


def test_point_force_rank_and_null_space_change_at_coincident_contacts() -> None:
    for separation, expected_rank in ((0.2, 5), (0.0, 3)):
        left = np.array([separation / 2, 0, 0])
        right = -left
        point_map = np.block([[np.eye(3), np.eye(3)], [_cross_matrix(left), _cross_matrix(right)]])
        assert np.linalg.matrix_rank(point_map) == expected_rank
        axial_pair = np.array([1, 0, 0, -1, 0, 0])
        assert point_map @ axial_pair == pytest.approx(np.zeros(6))
        axial_measurement = axial_pair[None, :] / 2
        augmented = np.vstack([point_map, axial_measurement])
        assert np.linalg.matrix_rank(augmented) == expected_rank + 1
        moment_columns = np.vstack([np.zeros((3, 6)), np.tile(np.eye(3), (1, 2))])
        assert np.linalg.matrix_rank(np.column_stack([point_map, moment_columns])) == 6


def test_common_force_changes_arbitrary_origin_moment_but_not_midpoint_couple() -> None:
    midpoint = np.array([0, 1, 0])
    separation = np.array([0.2, 0, 0])
    differential = np.array([0, 50, 0])
    common = np.array([100, 0, 0])
    left, right = midpoint + separation / 2, midpoint - separation / 2
    moment = np.cross(left, common + differential) + np.cross(right, common - differential)
    couple = np.cross(separation, differential)
    assert couple == pytest.approx([0, 0, 10])
    assert moment == pytest.approx([0, 0, -190])
    assert moment == pytest.approx(np.cross(midpoint, 2 * common) + couple)


def test_wrench_transport_preserves_rigid_power_for_one_observer() -> None:
    force, moment = np.array([3, 4, 5]), np.array([-2, 1, 6])
    velocity, angular_velocity = np.array([2, -1, 3]), np.array([1, 2, -1])
    offset = np.array([0.1, -0.2, 0.3])
    shifted_moment = moment - np.cross(offset, force)
    shifted_velocity = velocity + np.cross(angular_velocity, offset)
    assert force @ velocity + moment @ angular_velocity == pytest.approx(
        force @ shifted_velocity + shifted_moment @ angular_velocity
    )


def test_zero_wrench_can_have_deformation_power() -> None:
    left, right = np.array([0.1, 0, 0]), np.array([-0.1, 0, 0])
    force = np.array([10, 0, 0])
    assert np.cross(left, force) + np.cross(right, -force) == pytest.approx(np.zeros(3))
    assert force + (-force) == pytest.approx(np.zeros(3))
    # Separating endpoints cannot be represented by one rigid velocity field.
    assert force @ np.array([1, 0, 0]) + (-force) @ np.array([-1, 0, 0]) == 20


def test_negative_moment_projection_does_not_determine_total_power() -> None:
    moment, angular_velocity = np.array([-1, 2, 0]), np.array([1, 2, 0])
    normal = np.array([1, 0, 0])
    assert (moment @ normal) * (angular_velocity @ normal) == -1
    assert moment @ angular_velocity == 3


def test_zero_any_contact_transition_count_does_not_mean_all_stations_closed() -> None:
    counts = np.array([2, 1, 2, 1])
    any_active = counts > 0
    assert np.count_nonzero(any_active[1:] != any_active[:-1]) == 0
    assert np.count_nonzero(counts[1:] != counts[:-1]) == 3
    assert np.mean(counts < 2) == 0.5


def test_component_rmse_and_vector_percentile_are_distinct_metrics() -> None:
    errors = np.tile(np.array([3, 4, 0, 0, 0, 0]), (4, 1))
    assert np.sqrt(np.mean(errors**2)) == pytest.approx(5 / np.sqrt(6))
    assert np.percentile(np.linalg.norm(errors, axis=1), 95) == 5


@pytest.mark.parametrize(
    ("required", "forbidden"),
    [
        ("rank drops to three", "map has rank\nfive, not six"),
        ("contact midpoint", "common mode resembles their average"),
        ("rigid velocity field", "other powers and inertial terms remain"),
        ("bounded forces", "controls are decisive"),
        ("any station is active", "No contact opened during these runs"),
        ("0.5 ms", "description is converging rather than drifting"),
        ("component-wise RMSE", "combined registered case yields"),
        ("Choi and Park", "Bilateral grip sensors have demonstrated"),
    ],
)
def test_chapter_retains_explicit_mechanical_and_evidence_boundaries(
    required: str, forbidden: str
) -> None:
    text = CHAPTER.read_text(encoding="utf-8")
    assert required in text
    assert forbidden not in text
