"""Independent mechanics checks for the superposition reference article."""

from pathlib import Path

import numpy as np
import pytest


def test_affine_accelerations_require_one_baseline_subtraction() -> None:
    drift, first, second = 4.0, 2.0, -3.0
    assert drift + first + second == (drift + first) + (drift + second) - drift
    assert drift + first + second != (drift + first) + (drift + second)


def test_body_velocity_transport_recovers_spatial_acceleration() -> None:
    omega = np.array([0.0, 0.0, 2.0])
    body_velocity = np.array([3.0, 0.0, 0.0])
    body_rate = -np.cross(omega, body_velocity)
    assert body_rate + np.cross(omega, body_velocity) == pytest.approx(np.zeros(3))
    assert np.linalg.norm(body_rate) == pytest.approx(6.0)


def test_spatial_inertia_matches_center_of_mass_kinetic_energy() -> None:
    mass = 2.0
    offset = np.array([0.2, -0.1, 0.3])
    x, y, z = offset
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    center_inertia = np.diag([0.2, 0.3, 0.4])
    origin_inertia = center_inertia + mass * skew.T @ skew
    spatial = np.block([[origin_inertia, mass * skew], [-mass * skew, mass * np.eye(3)]])
    omega = np.array([1.0, -2.0, 0.5])
    velocity = np.array([2.0, 1.0, -1.0])
    twist = np.concatenate([omega, velocity])
    center_velocity = velocity + np.cross(omega, offset)
    assert spatial == pytest.approx(spatial.T)
    assert np.all(np.linalg.eigvalsh(spatial) > 0)
    assert twist @ spatial @ twist == pytest.approx(
        omega @ center_inertia @ omega + mass * center_velocity @ center_velocity
    )


def test_two_link_inertia_includes_both_center_of_mass_terms() -> None:
    # Two uniform unit rods, each with unit mass, at q2 = 0.
    center_inertia, center_distance = 1.0 / 12.0, 0.5
    first = 2 * center_inertia + center_distance**2 + 1 + center_distance**2
    coupling = center_distance
    last = center_inertia + center_distance**2
    mass = np.array([[first + 2 * coupling, last + coupling], [last + coupling, last]])
    expected = np.array([[8.0 / 3.0, 5.0 / 6.0], [5.0 / 6.0, 1.0 / 3.0]])
    assert mass == pytest.approx(expected)
    assert mass[1, 1] > center_inertia


def test_article_does_not_promote_affinity_to_causal_or_neural_identification() -> None:
    source = (Path(__file__).resolve().parents[1] / "articles/superposition.qmd").read_text(
        encoding="utf-8"
    )
    assert "activation dependence must be checked" in source.lower()
    assert "the acceleration increment, not a unique input" in source
    assert "Dominant Attractor" not in source
    assert "m c^\\times \\\\ \nm c^\\times" not in source
