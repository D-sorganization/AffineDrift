"""Synthetic counterexamples for Chapter 15; no human or shaft calibration."""

import numpy as np
import pytest


def test_point_power_decomposition_does_not_add_modal_power_twice() -> None:
    translation = np.array([1.0, 2.0, 3.0])
    omega = np.array([0.1, 0.2, 0.3])
    offset = np.array([0.4, 0.5, 0.6])
    shape = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
    rates = np.array([0.5, -0.2])
    force = np.array([10.0, -5.0, 2.0])
    velocity = translation + np.cross(omega, offset) + shape @ rates
    modal_power = (shape.T @ force) @ rates
    rigid_power = force @ translation + np.cross(offset, force) @ omega
    assert force @ velocity == pytest.approx(5.35)
    assert modal_power == pytest.approx(0.01)
    assert rigid_power + modal_power == pytest.approx(force @ velocity)
    assert force @ velocity + modal_power != pytest.approx(force @ velocity)


def test_zero_resultant_wrench_can_supply_deformation_power() -> None:
    forces = np.array([[10.0, 0.0, 0.0], [-10.0, 0.0, 0.0]])
    positions = np.array([[1.5, 0.0, 0.0], [-1.5, 0.0, 0.0]])
    velocities = np.array([[2.0, 0.0, 0.0], [-2.0, 0.0, 0.0]])
    np.testing.assert_allclose(forces.sum(axis=0), 0)
    np.testing.assert_allclose(np.cross(positions, forces).sum(axis=0), 0)
    assert np.sum(forces * velocities) == pytest.approx(40.0)


def test_modal_reset_can_increase_energy_and_change_momentum() -> None:
    mass = np.array([[2.0, 0.8], [0.8, 1.0]])
    before = np.array([1.0, -0.5])
    after = np.array([1.0, 0.0])
    assert np.all(np.linalg.eigvalsh(mass) > 0)
    assert 0.5 * before @ mass @ before == pytest.approx(0.725)
    assert 0.5 * after @ mass @ after == pytest.approx(1.0)
    np.testing.assert_allclose(mass @ (after - before), [0.4, 0.5])


def test_stiffness_trend_depends_on_control_and_excitation() -> None:
    stiffness = np.array([100.0, 200.0])
    force_control_energy = 10.0**2 / (2 * stiffness)
    displacement_control_energy = stiffness * 0.1**2 / 2
    assert force_control_energy[0] > force_control_energy[1]
    assert displacement_control_energy[0] < displacement_control_energy[1]
    # Harmonic steady-state amplitude, m=1 kg, c=1 N s/m, omega=10 rad/s.
    stiffness = np.array([50.0, 100.0, 200.0])
    amplitude = 1 / np.sqrt((stiffness - 100) ** 2 + 100)
    assert amplitude[0] < amplitude[1] > amplitude[2]


def test_prescribed_cycle_closes_energy_independently() -> None:
    from scripts.shaft_energy_illustration import prescribed_cycle

    data = prescribed_cycle()
    time = data["time"]
    assert len(time) == 4001
    assert time[[0, -1]] == pytest.approx([0, 0.6])
    np.testing.assert_allclose(
        np.gradient(data["displacement"], time)[1:-1], data["velocity"][1:-1], atol=6e-8, rtol=0
    )
    assert np.all(data["dissipation"] >= 0)
    assert data["input_power"].min() < -0.01 < 0.01 < data["input_power"].max()
    power = data["input_power"] - data["dissipation"]
    integrated = np.r_[0, np.cumsum((power[1:] + power[:-1]) * np.diff(time) / 2)]
    energy = data["elastic"] + data["kinetic"]
    np.testing.assert_allclose(integrated, energy - energy[0], atol=2e-8, rtol=0)
    np.testing.assert_allclose(data["energy_rate"], power, atol=1e-14)
    assert energy[-1] == pytest.approx(energy[0], abs=1e-15)


def test_club_frame_translation_omits_head_rotation_and_flexure() -> None:
    origin_velocity = np.array([1.0, 0.0, 0.0])
    omega = np.array([0.0, 2.0, 0.0])
    head_offset = np.array([0.0, 0.0, -1.0])
    flexible_velocity = np.array([-0.2, 0.0, 0.0])
    head_velocity = origin_velocity + np.cross(omega, head_offset) + flexible_velocity
    assert np.linalg.norm(origin_velocity) == pytest.approx(1.0)
    assert np.linalg.norm(head_velocity) == pytest.approx(1.2)
