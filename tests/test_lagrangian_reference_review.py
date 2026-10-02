"""Manufactured mechanics checks; these do not validate a human swing model."""

from pathlib import Path

import numpy as np
import pytest

MASS = np.array([[2.0, 0.4], [0.4, 0.8]])
INPUT_MAP = np.array([1.0, 0.0])
POSITION = np.array([0.2, -0.1])
VELOCITY = np.array([1.0, 2.0])
STIFFNESS = np.diag([3.0, 5.0])
DAMPING = np.diag([0.2, 0.1])
GRAVITY_M_S2 = 9.81


@pytest.mark.integration
def test_lagrangian_reference_links_primary_mechanics_and_normative_notation() -> None:
    source = Path("articles/lagrangian-reference.qmd").read_text(encoding="utf-8")
    assert "https://underactuated.mit.edu/multibody.html" in source
    assert "https://modernrobotics.northwestern.edu/nu-gm-book-resource/" in source
    assert "../pages/notation.html" in source


def test_damping_is_counted_once_in_the_energy_balance() -> None:
    # One angular coordinate: inertia 2, stiffness 3, damping 0.2 in SI units.
    acceleration = (-3 * 0.2 - 0.2 * 1) / 2
    assert acceleration == pytest.approx(-0.4)
    energy_rate = 2 * 1 * acceleration + 3 * 0.2 * 1
    assert energy_rate == pytest.approx(-0.2)


def test_unactuated_flexible_coordinate_receives_input_acceleration() -> None:
    np.testing.assert_allclose(np.linalg.solve(MASS, INPUT_MAP), [5 / 9, -5 / 18])
    applied = INPUT_MAP * 4
    acceleration = np.linalg.solve(MASS, applied - STIFFNESS @ POSITION - DAMPING @ VELOCITY)
    np.testing.assert_allclose(acceleration, [61 / 36, -17 / 36])
    energy_rate = VELOCITY @ (MASS @ acceleration + STIFFNESS @ POSITION)
    assert energy_rate == pytest.approx(3.4)
    assert energy_rate == pytest.approx(VELOCITY @ applied - VELOCITY @ DAMPING @ VELOCITY)


def test_affine_input_increment_does_not_double_total_acceleration() -> None:
    # Columns share a complete state; they are not separately evolved trajectories.
    retained_load = STIFFNESS @ POSITION + DAMPING @ VELOCITY
    loads = INPUT_MAP[:, None] * np.array([0, 4, 8]) - retained_load[:, None]
    accelerations = np.linalg.solve(MASS, loads)
    zero, four, eight = accelerations.T
    np.testing.assert_allclose(eight - zero, 2 * (four - zero))
    assert not np.allclose(eight, 2 * four)


def test_constraint_reaction_and_projected_input_map() -> None:
    mass = np.diag([2.0, 3.0])
    jacobian = np.array([[1.0, -1.0]])
    kkt = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    solution = np.linalg.solve(kkt, [10, 0, 0])
    np.testing.assert_allclose(solution, [2, 2, -6])
    powers = (jacobian.T[:, 0] * solution[2]) * np.array([0.4, 0.4])
    np.testing.assert_allclose(powers, [-2.4, 2.4])
    assert powers.sum() == pytest.approx(0)
    free_map = np.linalg.solve(mass, INPUT_MAP)
    reaction_map = np.linalg.solve(mass, jacobian.T)
    projected = free_map - reaction_map @ np.linalg.solve(
        jacobian @ reaction_map, jacobian @ free_map
    )
    np.testing.assert_allclose(projected, [0.2, 0.2])
    np.testing.assert_allclose(jacobian @ projected, 0, atol=1e-14)


def test_moving_support_supplies_power_and_precludes_zero_velocity_reset() -> None:
    mass = 2.0
    speed, acceleration = 0.3, 0.4
    support_force = mass * (acceleration + GRAVITY_M_S2)
    assert support_force == pytest.approx(20.42)
    power = support_force * speed
    assert power == pytest.approx(6.126)
    assert power == pytest.approx(mass * speed * acceleration + mass * GRAVITY_M_S2 * speed)
    assert abs(0 - speed) == pytest.approx(0.3)  # Defect in the prescribed velocity constraint.


def test_variable_inertia_energy_derivative_includes_velocity_product() -> None:
    position, velocity, damping, torque = 0.4, -1.2, 0.2, 1.7
    inertia = 2 + np.cos(position)
    velocity_product = -0.5 * np.sin(position) * velocity**2
    gradient = 3 * np.sin(position)
    acceleration = (torque - velocity_product - gradient - damping * velocity) / inertia
    step = 1e-7  # Central directional derivative, not a time-integrated simulation.
    positions = position + np.array([-step, step]) * velocity
    velocities = velocity + np.array([-step, step]) * acceleration
    energies = 0.5 * (2 + np.cos(positions)) * velocities**2 + 3 * (1 - np.cos(positions))
    derivative = np.diff(energies).item() / (2 * step)
    assert derivative == pytest.approx(torque * velocity - damping * velocity**2, abs=1e-7)
    assert derivative == pytest.approx(-2.328, abs=1e-7)


def test_zero_command_retains_actuator_load() -> None:
    initial_torque, time_constant, inertia = 6.0, 0.03, 2.0
    times = np.array([0, time_constant])
    torque = initial_torque * np.exp(-times / time_constant)
    np.testing.assert_allclose(torque, [6, 6 / np.e])
    assert np.all(torque / inertia > 0)
    assert 0 / inertia == 0  # A direct applied-torque removal is a different intervention.


def test_zero_velocity_drift_sign_differs_from_holding_load() -> None:
    holding_load = STIFFNESS @ POSITION
    drift_load = -holding_load
    np.testing.assert_allclose(drift_load, [-0.6, 0.5])
    acceleration = np.linalg.solve(MASS, drift_load)
    np.testing.assert_allclose(acceleration, [-17 / 36, 31 / 36])
    np.testing.assert_allclose(MASS @ acceleration + holding_load, 0, atol=1e-14)
    assert holding_load[1] != 0  # The sole first-coordinate actuator cannot hold this state.
