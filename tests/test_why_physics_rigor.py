"""Independent mechanics checks for the paired opening chapter and its figure."""

import importlib
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).parents[1]
BOOK = ROOT / "articles/The_Physics_of_Golf"
EDITIONS = ("quarto/ch01_why_physics.qmd", "chapters/ch01_why_physics.tex")


@pytest.fixture
def figure():
    return importlib.import_module("scripts.build_why_physics_figure")


@pytest.mark.parametrize("edition", EDITIONS)
@pytest.mark.parametrize(
    "obsolete",
    (
        "has nothing to do with muscle contraction",
        "realistic golf parameters",
        "all forces in your swing come from one of two sources",
        "70--80%",
        "179g",
        "Elite golfers, we'll find, have high DCR",
    ),
)
def test_paired_chapter_removes_identified_misconceptions(edition, obsolete):
    assert obsolete not in (BOOK / edition).read_text(encoding="utf-8")


def test_figure_retains_radius_and_conserves_energy(figure):
    data = figure.trajectory_data()
    position = data["retained"]
    np.testing.assert_allclose(np.linalg.norm(position, axis=1), 1.25, atol=1e-12)
    # Cartesian finite differences independently check the integrated angular model.
    velocity = np.gradient(position, data["time"], axis=0, edge_order=2)
    kinetic = 0.5 * 0.2 * np.sum(velocity**2, axis=1)
    total = kinetic + 0.2 * 9.81 * position[:, 1]
    np.testing.assert_allclose(total[2:-2], 157.5475, atol=0.002)
    # A unilateral tether remains feasible: it never needs to push the mass.
    tension = 0.2 * (np.sum(velocity**2, axis=1) / 1.25 - 9.81 * position[:, 1] / 1.25)
    assert np.min(tension) > 0


@pytest.mark.parametrize("edition", EDITIONS)
def test_both_editions_publish_the_checked_budget(edition):
    source = (BOOK / edition).read_text(encoding="utf-8")
    for number in ("1280", "130.48", "257.962", "160", "1.962", "4.429", "81.55", "0.4515"):
        assert number in source


def test_figure_starts_at_same_state_but_release_changes_acceleration(figure):
    data = figure.trajectory_data()
    np.testing.assert_allclose(data["retained"][0], data["released"][0])
    for key in ("retained", "released"):
        velocity = np.gradient(data[key], data["time"], axis=0, edge_order=2)
        np.testing.assert_allclose(velocity[0], [40, 0], atol=0.001)
    free_acceleration = np.gradient(
        np.gradient(data["released"], data["time"], axis=0), data["time"], axis=0
    )
    np.testing.assert_allclose(free_acceleration[2:-2, 0], 0, atol=1e-6)
    np.testing.assert_allclose(free_acceleration[2:-2, 1], -9.81, atol=1e-6)
    assert data["retained"][-1, 1] > 0
    assert data["released"][-1, 1] < -1.25


def test_bottom_force_balance_has_large_normal_acceleration_and_zero_power():
    mass, speed, radius, gravity = 0.2, 40.0, 1.25, 9.81
    tension = mass * (speed**2 / radius + gravity)
    force = np.array([0, tension - mass * gravity])
    assert tension == pytest.approx(257.962)
    np.testing.assert_allclose(force / mass, [0, 1280])
    assert force @ [speed, 0] == 0
    assert speed**2 / radius / gravity == pytest.approx(130.479102956)


def test_gravity_budget_depends_on_height_not_a_drift_percentage():
    mass, gravity, height = 0.2, 9.81, 1.0
    work = mass * gravity * height
    assert work == pytest.approx(1.962)
    assert np.sqrt(2 * work / mass) == pytest.approx(4.429446918)
    assert 40**2 / (2 * gravity) == pytest.approx(81.5494393476)
    assert 0.5 * mass * 40**2 == 160


def test_input_baseline_changes_attribution_without_changing_acceleration():
    drift, gain, torque, baseline = -2.0, 0.5, 6.0, 4.0
    original = drift + gain * torque
    shifted_drift, residual = drift + gain * baseline, torque - baseline
    assert original == shifted_drift + gain * residual == 1.0
    assert abs(drift) / abs(gain * torque) == pytest.approx(2 / 3)
    assert abs(shifted_drift) / abs(gain * residual) == 0


def test_radial_retraction_can_supply_power_without_pivot_torque():
    position, force, velocity = np.array([2.0, 0]), np.array([-5.0, 0]), [-0.3, 4]
    moment = position[0] * force[1] - position[1] * force[0]
    assert moment == 0
    assert force @ velocity == pytest.approx(1.5)


def test_zero_net_joint_torque_does_not_identify_muscle_forces():
    moment_arms = np.array([0.03, -0.03])
    assert moment_arms @ [0, 0] == moment_arms @ [100, 100] == 0


def test_build_figure_writes_both_vector_formats(figure, tmp_path):
    figure.build_figure(tmp_path)
    assert (tmp_path / "why_physics_release.svg").read_text().count("<svg") == 1
    assert b"\r\n" not in (tmp_path / "why_physics_release.svg").read_bytes()
    assert (tmp_path / "why_physics_release.pdf").read_bytes().startswith(b"%PDF")
