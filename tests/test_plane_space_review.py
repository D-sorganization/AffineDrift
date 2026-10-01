"""Observer, projection and evidence boundaries for companion Chapter 20."""

from pathlib import Path

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/proximal_distal_companion/chapters/ch20_plane_to_space.qmd"
)


def test_passive_rotation_preserves_power_but_observer_boost_does_not() -> None:
    force = np.array([2.0, -3.0, 4.0])
    moment = np.array([1.0, 5.0, -2.0])
    velocity = np.array([3.0, 1.0, -1.0])
    angular_velocity = np.array([0.5, -0.2, 0.3])
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    power = force @ velocity + moment @ angular_velocity
    rotated = (rotation @ force) @ (rotation @ velocity)
    rotated += (rotation @ moment) @ (rotation @ angular_velocity)
    assert rotated == pytest.approx(power)
    observer_velocity = np.array([2.0, 0.0, 0.0])
    moving_power = force @ (velocity - observer_velocity) + moment @ angular_velocity
    assert moving_power == pytest.approx(power - force @ observer_velocity)
    assert moving_power != pytest.approx(power)


def test_small_axis_change_can_reverse_a_near_zero_projection() -> None:
    moment = np.array([1.0, 0.0, -0.01])
    normal = np.array([0.0, 0.0, 1.0])
    angle = np.deg2rad(1.0)
    changed_normal = np.array([np.sin(angle), 0.0, np.cos(angle)])
    assert moment @ normal < 0 < moment @ changed_normal
    bound = 2 * np.linalg.norm(moment) * np.sin(angle / 2)
    assert abs(moment @ (changed_normal - normal)) <= bound
    # A re-expression rotates both vectors; choosing another physical axis does not.
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    assert (rotation @ moment) @ (rotation @ normal) == pytest.approx(moment @ normal)


def test_full_rank_open_constraint_does_not_prove_bounded_feasibility() -> None:
    jacobian = np.eye(2)
    target = np.array([2.0, 2.0])
    upper_bound = np.ones(2)
    assert np.linalg.matrix_rank(jacobian) == 2
    assert np.linalg.norm(jacobian @ upper_bound - target) > 1.0
    assert np.all(target > upper_bound)


@pytest.mark.parametrize(
    "boundary",
    [
        "same observer",
        "no independent contact moment",
        "0.5 mm",
        "39 of 54",
        "shared semi-implicit",
        "without advancing a new trajectory",
        "point-force moment",
        "not a closed planar dynamics model",
    ],
)
def test_chapter_states_mechanical_and_archive_boundaries(boundary: str) -> None:
    assert boundary in CHAPTER.read_text(encoding="utf-8")
