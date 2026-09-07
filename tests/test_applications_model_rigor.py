"""Independent energy checks for the applications teaching model."""

from dataclasses import replace

import numpy as np
import pytest

from src.affine_control.golf_model import SEGMENTS, GolfModel


@pytest.mark.parametrize("mode", [0, 1])
def test_mode_amplitude_is_the_signed_tip_displacement(mode: int) -> None:
    values = SEGMENTS.mode_shape(mode, np.array([0.0, SEGMENTS.lengths[2]]))
    np.testing.assert_allclose(values, [0.0, 1.0], atol=1e-9)


def test_full_inertia_accounts_for_every_shaft_material_point() -> None:
    q = np.array([0.4, -0.7, 0.2])
    velocity = np.array([0.8, -0.5, 0.9, 0.06, -0.02])
    samples = 4001
    s = np.linspace(0.0, SEGMENTS.lengths[2], samples)
    angles = np.cumsum(q)
    normal = np.array([-np.sin(angles[-1]), np.cos(angles[-1])])
    handle_velocity = np.zeros(2)
    for index in range(2):
        handle_velocity += (
            SEGMENTS.lengths[index]
            * np.sum(velocity[: index + 1])
            * np.array([-np.sin(angles[index]), np.cos(angles[index])])
        )
    bending_rate = sum(SEGMENTS.mode_shape(mode, s) * velocity[3 + mode] for mode in range(2))
    material_velocity = handle_velocity[:, None] + normal[:, None] * (
        np.sum(velocity[:3]) * s + bending_rate
    )
    shaft_energy = (
        0.5
        * SEGMENTS.shaft_mass
        / SEGMENTS.lengths[2]
        * np.trapezoid(np.sum(material_velocity**2, axis=0), s)
    )
    rigid_energy = 0.5 * velocity[:3] @ SEGMENTS.rigid_mass_matrix(q) @ velocity[:3]
    assembled_energy = 0.5 * velocity @ SEGMENTS.full_mass_matrix(q, samples) @ velocity
    assert assembled_energy == pytest.approx(rigid_energy + shaft_energy, rel=1e-11)


def test_added_shaft_mass_changes_rotational_inertia() -> None:
    q = np.array([0.4, -0.7, 0.2])
    heavy = replace(SEGMENTS, shaft_mass=2 * SEGMENTS.shaft_mass)
    increment = heavy.full_mass_matrix(q) - SEGMENTS.full_mass_matrix(q)
    expected_distal = SEGMENTS.shaft_mass * SEGMENTS.lengths[2] ** 2 / 3
    assert increment[2, 2] == pytest.approx(expected_distal, rel=1e-6)
    assert np.linalg.eigvalsh(increment).min() > -1e-10


def test_a_light_carrier_does_not_make_a_positive_mass_shaft_indefinite() -> None:
    model = GolfModel(masses=(0.01, 0.01, 0.01), inertias=(0.001, 0.001, 0.001))
    assert np.linalg.eigvalsh(model.full_mass_matrix(np.zeros(3))).min() > 0


def test_rigid_counterfactual_preserves_its_declared_mechanical_energy() -> None:
    q = np.array([0.4, -0.7, 0.2])
    velocity = np.array([0.8, -0.5, 0.9])
    step = 1e-6
    mass = SEGMENTS.rigid_mass_matrix(q)
    mass_rate = (
        SEGMENTS.rigid_mass_matrix(q + step * velocity)
        - SEGMENTS.rigid_mass_matrix(q - step * velocity)
    ) / (2 * step)
    potential_rate = (
        SEGMENTS.potential_energy(q + step * velocity)
        - SEGMENTS.potential_energy(q - step * velocity)
    ) / (2 * step)
    energy_rate = (
        velocity @ mass @ SEGMENTS.drift_acceleration(q, velocity)
        + 0.5 * velocity @ mass_rate @ velocity
        + potential_rate
    )
    assert energy_rate == pytest.approx(0, abs=1e-7)


def test_modal_spring_is_symmetric_and_positive() -> None:
    stiffness = SEGMENTS.modal_stiffness()
    np.testing.assert_allclose(stiffness, stiffness.T, atol=1e-12)
    assert np.linalg.eigvalsh(stiffness).min() > 0
