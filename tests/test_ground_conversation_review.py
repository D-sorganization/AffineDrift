"""Independent counterexamples for ground power and archived matching claims."""

from pathlib import Path

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/proximal_distal_companion/chapters/ch16_ground_conversation.qmd"
)


def test_symmetric_difference_does_not_measure_energy_ratio() -> None:
    ratios = np.array([2.0, 13.440918029187419, 3519.398873370441])
    difference = 2 * (ratios - 1) / (ratios + 1)
    assert difference[0] == pytest.approx(2 / 3)
    assert difference[1:] == pytest.approx([1.7230092995531614, 1.9988637651175676])
    assert np.all(difference < 2)
    assert (2 + difference) / (2 - difference) == pytest.approx(ratios)


def test_pressure_center_can_move_while_contact_material_is_stationary() -> None:
    positions = np.array([-0.1, 0.1])
    loads = np.array([[300.0, 100.0], [100.0, 300.0]])
    pressure_centers = loads @ positions / loads.sum(axis=1)
    material_velocities = np.zeros_like(loads)
    assert pressure_centers == pytest.approx([-0.05, 0.05])
    assert np.sum(loads * material_velocities) == 0


def test_control_and_velocity_counterfactuals_overlap() -> None:
    configuration, velocity, control, external = 10.0, 4.0, -3.0, 2.0
    total = configuration + velocity + control + external
    ztcf = configuration + velocity + external
    zvcf = configuration + external
    assert total - ztcf == control
    assert ztcf - zvcf == velocity
    assert ztcf + zvcf != total


@pytest.mark.parametrize(
    "boundary",
    [
        "material-point velocity",
        "body-plus-club",
        "zero-velocity control-preserved",
        "full row rank",
        "13.44 to 3519.40",
        "48, 8, 4, and 0",
        "declared primary criterion",
        "shared contact law",
        "surface-normal free moment",
    ],
)
def test_chapter_states_corrected_mechanical_and_archive_boundaries(boundary: str) -> None:
    assert boundary in " ".join(CHAPTER.read_text(encoding="utf-8").split())
