"""Independent mechanical checks for the bounded club-fitting explanation."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest

ARTICLE = Path(__file__).resolve().parents[1] / "articles/technology-club-fitting.qmd"


def test_point_shift_and_dual_wrench_preserve_power() -> None:
    angular = np.array([0.0, 0.0, 2.0])
    offset = np.array([0.3, 0.0, 0.0])
    velocity_a = np.array([1.0, 2.0, 3.0])
    force = np.array([4.0, 5.0, 6.0])
    moment_a = np.array([7.0, 8.0, 9.0])
    velocity_b = velocity_a + np.cross(angular, offset)
    moment_b = moment_a - np.cross(offset, force)
    assert velocity_b == pytest.approx([1.0, 2.6, 3.0])
    assert angular @ moment_a + velocity_a @ force == pytest.approx(
        angular @ moment_b + velocity_b @ force
    )


def _tetrahedron_surface_moments(translation: np.ndarray) -> tuple[float, np.ndarray]:
    vertices = np.vstack([np.zeros(3), np.eye(3)]) + translation
    faces = vertices[np.array([[1, 2, 3], [0, 2, 1], [0, 1, 3], [0, 3, 2]])]
    signed_volumes = np.einsum("ij,ij->i", faces[:, 0], np.cross(faces[:, 1], faces[:, 2])) / 6
    first_moment = np.sum(signed_volumes[:, None] * np.sum(faces, axis=1) / 4, axis=0)
    return float(np.sum(signed_volumes)), first_moment


@pytest.mark.parametrize("translation", [np.zeros(3), np.array([2.0, -3.0, 4.0])])
def test_signed_tetrahedra_reproduce_volume_and_translated_centroid(
    translation: np.ndarray,
) -> None:
    volume, first_moment = _tetrahedron_surface_moments(translation)
    assert volume == pytest.approx(1 / 6)
    assert first_moment / volume == pytest.approx(translation + 0.25)


def test_tetrahedron_centroid_inertia_matches_analytic_integrals() -> None:
    # On the unit simplex: integral x^2 = 1/60, integral xy = 1/120.
    inertia_origin = np.full((3, 3), -1 / 120)
    np.fill_diagonal(inertia_origin, 1 / 30)
    center = np.full(3, 0.25)
    inertia_center = (
        inertia_origin - (np.dot(center, center) * np.eye(3) - np.outer(center, center)) / 6
    )
    assert np.diag(inertia_center) == pytest.approx(np.full(3, 1 / 80))
    assert inertia_center[0, 1] == pytest.approx(1 / 480)
    assert np.linalg.eigvalsh(inertia_center) == pytest.approx([1 / 96, 1 / 96, 1 / 60])


def test_radial_steady_rotation_tension_has_force_scale() -> None:
    mass_per_length, length, root_radius, angular_speed, head_mass = 0.06, 1.1, 0.2, 40.0, 0.2
    shaft_force = mass_per_length * angular_speed**2 * (root_radius * length + length**2 / 2)
    head_force = head_mass * angular_speed**2 * (root_radius + length)
    assert shaft_force == pytest.approx(79.2)
    assert shaft_force + head_force == pytest.approx(495.2)


def test_cantilever_tip_compliance_needs_rotation_translation_coupling() -> None:
    length, rigidity, force = 1.0, 20.0, 3.0
    stiffness = rigidity / length**3 * np.array([[12.0, -6 * length], [-6 * length, 4 * length**2]])
    displacement, slope = np.linalg.solve(stiffness, [force, 0.0])
    assert displacement == pytest.approx(force * length**3 / (3 * rigidity))
    assert slope == pytest.approx(force * length**2 / (2 * rigidity))
    assert force / stiffness[0, 0] == pytest.approx(displacement / 4)


def test_torsion_uses_torque_and_polar_rigidity() -> None:
    torque, length, rigidity = 2.0, 1.0, 10.0
    angle = torque * length / rigidity
    stored_energy = rigidity * angle**2 / (2 * length)
    assert angle == pytest.approx(0.2)
    assert stored_energy == pytest.approx(torque * angle / 2)


def test_rotated_component_inertia_preserves_energy() -> None:
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    local_inertia = np.diag([1.0, 2.0, 3.0])
    angular_world = np.array([2.0, 3.0, 4.0])
    world_inertia = rotation @ local_inertia @ rotation.T
    angular_local = rotation.T @ angular_world
    assert angular_world @ world_inertia @ angular_world == pytest.approx(
        angular_local @ local_inertia @ angular_local
    )


def test_mean_confidence_interval_is_not_shot_dispersion() -> None:
    known_sigma, sample_count, normal_quantile = 4.2, 25, 1.96
    mean_half_width = normal_quantile * known_sigma / np.sqrt(sample_count)
    population_half_width = normal_quantile * known_sigma
    assert mean_half_width == pytest.approx(1.6464)
    assert population_half_width == pytest.approx(8.232)


@pytest.mark.parametrize(
    "required",
    [
        r"-[\mathbf{r}_{B/A}]_\times",
        r"\Delta V_k=\frac{1}{6}",
        "residual is not an identified neural adaptation",
        "proposed data examples",
        r"\mu_\theta",
        "off-diagonal",
    ],
)
def test_article_corrects_sign_factors_and_inference_contract(required: str) -> None:
    assert required in ARTICLE.read_text(encoding="utf-8")


def test_proposed_json_examples_are_synthetic_and_do_not_assert_a_missing_schema() -> None:
    documents = [
        json.loads(s)
        for s in re.findall(r"```json\s*\n(.*?)\n```", ARTICLE.read_text(encoding="utf-8"), re.S)
    ]
    assert len(documents) == 3
    assert all(
        document["example_status"] == "synthetic_not_a_validated_run" for document in documents
    )
    assert all("$schema" not in document for document in documents)
    trajectory = documents[1]
    for sample in trajectory["trajectory_samples"]:
        assert np.linalg.norm(sample["orientation_quaternion_wxyz"]) == pytest.approx(1.0)
    assert trajectory["velocity_reference_point"] == "head_center_of_mass"
    assert trajectory["velocity_expressed_in"] == "world"
