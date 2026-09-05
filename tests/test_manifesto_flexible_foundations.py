"""Independent mechanics examples for manifesto foundation correction #4187."""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

Array = NDArray[np.float64]
ROOT = Path(__file__).resolve().parents[1]


def rotation(angle: float) -> Array:
    """Map planar body components into world components."""
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]])


def point(state: Array, station: float) -> Array:
    """Position for translation, hand angle, and one clamped bending coordinate."""
    translation, angle, modal = state
    return np.array([translation, 0.0]) + rotation(angle) @ np.array([station, station**2 * modal])


def point_jacobian(state: Array, station: float) -> Array:
    """Differentiate the complete placement, retaining orientation and bending."""
    _, angle, modal = state
    return np.column_stack(
        (
            [1.0, 0.0],
            rotation(angle) @ np.array([-(station**2) * modal, station]),
            rotation(angle) @ np.array([0.0, station**2]),
        )
    )


def head_position(state: Array) -> Array:
    """Place the head center of mass at an offset from the shaft tip."""
    return point(state, 1.0) + rotation(state[1] + 2 * state[2]) @ np.array([0.1, 0.05])


def head_jacobian(state: Array) -> Array:
    """Use the declared small-slope head orientation model."""
    tangent = rotation(state[1] + 2 * state[2]) @ np.array([-0.05, 0.1])
    return point_jacobian(state, 1.0) + np.outer(tangent, [0.0, 1.0, 2.0])


def mass_matrix(state: Array) -> Array:
    """Assemble shaft, head translation/rotation, and supporting rigid inertia."""
    nodes, weights = np.polynomial.legendre.leggauss(8)
    matrix = np.diag([1.0, 0.2, 0.0])
    for station, weight in zip((nodes + 1) / 2, weights / 2, strict=True):
        jacobian = point_jacobian(state, float(station))
        matrix += 0.1 * weight * jacobian.T @ jacobian
    head = head_jacobian(state)
    angular = np.array([0.0, 1.0, 2.0])
    return matrix + 0.2 * head.T @ head + 0.03 * np.outer(angular, angular)


def test_world_point_jacobian_matches_full_placement_derivative() -> None:
    state = np.array([0.3, 0.7, 0.04])
    step = 1e-6
    differences = np.column_stack(
        [
            (point(state + step * unit, 0.8) - point(state - step * unit, 0.8)) / (2 * step)
            for unit in np.eye(3)
        ]
    )
    np.testing.assert_allclose(point_jacobian(state, 0.8), differences, atol=1e-10)
    assert point_jacobian(state, 0.8)[0, 2] != pytest.approx(0.0)
    assert not np.allclose(
        point_jacobian(state, 0.8)[:, 1], point_jacobian(np.array([0.3, 0.7, 0.0]), 0.8)[:, 1]
    )


def test_head_center_of_mass_is_not_the_shaft_tip() -> None:
    state = np.array([0.3, 0.7, 0.04])
    step = 1e-6
    differences = np.column_stack(
        [
            (head_position(state + step * unit) - head_position(state - step * unit)) / (2 * step)
            for unit in np.eye(3)
        ]
    )
    np.testing.assert_allclose(head_jacobian(state), differences, atol=1e-10)
    assert not np.allclose(head_jacobian(state), point_jacobian(state, 1.0))


def test_assembled_mass_matches_direct_kinetic_energy() -> None:
    state, velocity = np.array([0.3, 0.7, 0.04]), np.array([0.6, 1.2, -0.3])
    nodes, weights = np.polynomial.legendre.leggauss(12)
    energy = 0.5 * (velocity[0] ** 2 + 0.2 * velocity[1] ** 2)
    for station, weight in zip((nodes + 1) / 2, weights / 2, strict=True):
        speed = point_jacobian(state, float(station)) @ velocity
        energy += 0.5 * 0.1 * weight * (speed @ speed)
    head_speed = head_jacobian(state) @ velocity
    energy += 0.5 * 0.2 * (head_speed @ head_speed)
    energy += 0.5 * 0.03 * (velocity[1] + 2 * velocity[2]) ** 2
    mass = mass_matrix(state)
    np.testing.assert_allclose(mass, mass.T, atol=1e-14)
    assert np.linalg.eigvalsh(mass).min() > 0
    assert 0.5 * velocity @ mass @ velocity == pytest.approx(energy)


def test_coupling_changes_with_posture_without_changing_equipment() -> None:
    matrices = [mass_matrix(np.array([0.0, angle, 0.02])) for angle in [0.0, np.pi / 2]]
    couplings = [-matrix[2, :2] / matrix[2, 2] for matrix in matrices]
    assert not np.allclose(couplings[0], couplings[1])


def test_schur_complement_recovers_input_acceleration() -> None:
    mass = mass_matrix(np.array([0.3, 0.7, 0.04]))
    coupling = -mass[2:3, :2] / mass[2, 2]
    schur = mass[:2, :2] + mass[:2, 2:3] @ coupling
    joint = np.linalg.solve(schur, [0.8, -0.4])
    assembled = np.concatenate((joint, coupling @ joint))
    np.testing.assert_allclose(assembled, np.linalg.solve(mass, [0.8, -0.4, 0.0]))


def test_schur_reduction_need_not_be_strict_in_every_direction() -> None:
    rigid, cross, modal = np.eye(2) * 3, np.array([[0.5], [0.0]]), 2.0
    schur = rigid - cross @ cross.T / modal
    np.testing.assert_allclose(np.linalg.eigvalsh(rigid - schur), [0.0, 0.125])
    assert schur[1, 1] == rigid[1, 1]


def test_total_modal_acceleration_retains_modal_bias() -> None:
    mass = mass_matrix(np.array([0.3, 0.7, 0.04]))
    bias = np.array([0.2, 0.1, 0.8])
    acceleration = np.linalg.solve(mass, np.array([0.8, -0.4, 0.0]) - bias)
    transmitted = -mass[2, :2] @ acceleration[:2] / mass[2, 2]
    assert acceleration[2] == pytest.approx(transmitted - bias[2] / mass[2, 2])
    assert acceleration[2] != pytest.approx(transmitted)


def test_passive_joint_load_cannot_disappear_from_drift() -> None:
    mass = mass_matrix(np.array([0.3, 0.7, 0.04]))
    base = np.array([0.2, 0.1, 0.8])
    passive = np.array([0.0, 0.5, 0.0])
    full = np.linalg.solve(mass, -base - passive)
    omitted = np.linalg.solve(mass, -base)
    np.testing.assert_allclose(full - omitted, -np.linalg.solve(mass, passive))
    assert not np.allclose(full, omitted)


def test_modal_normalization_changes_coefficients_not_physical_energy() -> None:
    mass = mass_matrix(np.array([0.3, 0.7, 0.04]))
    basis_change = np.diag([1.0, 1.0, 10.0])
    transformed = basis_change.T @ mass @ basis_change
    velocity = np.array([0.6, 1.2, -0.3])
    new_velocity = np.linalg.solve(basis_change, velocity)
    assert new_velocity @ transformed @ new_velocity == pytest.approx(velocity @ mass @ velocity)
    np.testing.assert_allclose(
        -transformed[2, :2] / transformed[2, 2], -mass[2, :2] / mass[2, 2] / 10
    )


def test_nonlinear_coordinate_drift_includes_kinematic_acceleration() -> None:
    position, velocity, mass, force = 2.0, 3.0, 4.0, 5.0
    coordinate = position**2
    coordinate_velocity = 2 * position * velocity
    coordinate_acceleration = 2 * velocity**2 + 2 * position * force / mass
    metric = mass / (4 * coordinate)
    christoffel = -1 / (2 * coordinate)
    force_covector = force / (2 * position)
    assert coordinate_acceleration + christoffel * coordinate_velocity**2 == pytest.approx(
        force_covector / metric
    )
    assert force_covector * coordinate_velocity == pytest.approx(force * velocity)


@pytest.mark.parametrize("name", ["theory-part1", "drifter-manifesto", "affine-nature-golf-swing"])
def test_foundation_editions_retain_the_corrected_mechanical_scope(name: str) -> None:
    text = (ROOT / "articles" / f"{name}.qmd").read_text(encoding="utf-8")
    assert "A Rotating Flexible-Link Check" in text
    assert "center-of-mass Jacobian" in text
    assert "positive-semidefinite reduction" in text
    assert "input contribution, not the total modal acceleration" in text
    assert "making it a fixed property of the club's design" not in text
