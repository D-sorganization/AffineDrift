"""Manufactured Chapter 25 mechanics checks; no participant or physiological validation."""

import re
from pathlib import Path

import numpy as np
import pytest


@pytest.mark.parametrize("forces_y,couples_z", [((-10, 110), (0, 0)), ((30, 70), (4, 4))])
def test_full_wrench_and_power_match(forces_y: tuple[int, int], couples_z: tuple[int, int]) -> None:
    """Distinct bilateral loads give 100 N, 12 Nm and 236 W at the declared rigid twist."""
    positions = np.array([[-0.1, 0, 0], [0.1, 0, 0]])
    forces = np.array([[0, value, 0] for value in forces_y])
    couples = np.array([[0, 0, value] for value in couples_z])
    net_force = forces.sum(axis=0)
    net_moment = (np.cross(positions, forces) + couples).sum(axis=0)
    np.testing.assert_allclose(net_force, [0, 100, 0])
    np.testing.assert_allclose(net_moment, [0, 0, 12])

    # Common force is half the resultant at EACH hand, not their opposing difference.
    common = net_force / 2
    common_moment = np.cross(positions[0] + positions[1], common)
    np.testing.assert_allclose(common_moment, [0, 0, 0])

    v_origin, omega = np.array([0, 2, 0]), np.array([0, 0, 3])
    velocities = v_origin + np.cross(omega, positions)
    np.testing.assert_allclose(velocities[:, 1], [1.7, 2.3])
    local_power = np.sum(forces * velocities) + np.sum(couples * omega)
    expected_hand_power = [-17, 253] if forces_y == (-10, 110) else [63, 173]
    np.testing.assert_allclose(
        np.sum(forces * velocities, axis=1) + np.sum(couples * omega, axis=1),
        expected_hand_power,
    )
    assert local_power == pytest.approx(236)
    assert net_force @ v_origin + net_moment @ omega == pytest.approx(local_power)

    # Physically move contacts relative to the SAME origin; this is not origin transport.
    shifted = positions + np.array([0.02, 0, 0])
    shifted_moment = (np.cross(shifted, forces) + couples).sum(axis=0)
    np.testing.assert_allclose(shifted_moment, [0, 0, 14])


@pytest.mark.parametrize("antagonist", [-1, 0, 50, 100, 200, 201])
def test_bounded_allocation_and_signed_path_power(antagonist: float) -> None:
    """Force bounds restrict the torque null direction; net path power is not metabolism."""
    agonist = antagonist + 100
    feasible = 0 <= agonist <= 300 and 0 <= antagonist <= 200
    assert feasible == (0 <= antagonist <= 200)
    assert 0.03 * (agonist - antagonist) == pytest.approx(3)
    if feasible:
        length_rates = np.array([-0.06, 0.06])  # m/s at qdot=2 rad/s
        path_power = -np.array([agonist, antagonist]) @ length_rates
        assert path_power == pytest.approx(6)
        assert path_power == pytest.approx(3 * 2)


def test_strain_energy_and_series_elasticity() -> None:
    """Elastic force-extension laws store energy; no time delay is defined by these laws."""
    stiffness, start, end = 10000, 0.005, 0.01
    forces = stiffness * np.array([start, end])
    np.testing.assert_allclose(forces, [50, 100])
    energy_change = 0.5 * stiffness * (end**2 - start**2)
    trapezoid_work = forces.mean() * (end - start)
    assert energy_change == pytest.approx(0.375)
    assert trapezoid_work == pytest.approx(energy_change)

    # At a common 20 N, two series springs extend .02 + .01 = .03 m.
    extensions = 20 / np.array([1000, 2000])
    assert extensions.sum() == pytest.approx(0.03)
    equivalent_stiffness = 1 / (1 / 1000 + 1 / 2000)
    assert equivalent_stiffness == pytest.approx(2000 / 3)
    assert equivalent_stiffness * extensions.sum() == pytest.approx(20)


def _geometric_torque(angle: float, moment_arm_derivative: float) -> float:
    """Two preloaded tensile elastic paths; q is dimensionless radians near zero."""
    length_changes = np.array(
        [-0.03 * angle - 0.5 * moment_arm_derivative * angle**2, 0.03 * angle]
    )
    forces = 100 + 1000 * length_changes
    moment_arms = np.array([0.03 + moment_arm_derivative * angle, -0.03])
    return float(moment_arms @ forces)


@pytest.mark.parametrize("derivative,expected", [(0, 1.8), (0.02, -0.2)])
def test_geometric_stiffness_by_finite_difference(derivative: float, expected: float) -> None:
    """Positive material stiffness does not guarantee positive generalized stiffness."""
    analytic = 2 * 1000 * 0.03**2 - 100 * derivative
    assert analytic == pytest.approx(expected)
    assert _geometric_torque(0, derivative) == pytest.approx(0)
    for step in (1e-4, 1e-5, 1e-6):
        measured = -(_geometric_torque(step, derivative) - _geometric_torque(-step, derivative)) / (
            2 * step
        )
        assert measured == pytest.approx(expected, abs=1e-7)


@pytest.mark.integration
def test_provider_links_pin_the_reviewed_source() -> None:
    """The reviewed provider contract must not silently follow mutable main."""
    root = Path(__file__).resolve().parents[1]
    text = (
        root / "articles/proximal_distal_companion/chapters/ch25_biological_ambiguity.qmd"
    ).read_text(encoding="utf-8")
    links = re.findall(r"https://github.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert len(links) >= 2
    revision = "85cce4d3307bb7ad3953d9fc6e583e370803515c"
    assert all(re.search(rf"/blob/{revision}/", link) for link in links)
