"""Independent mechanics checks for the energy-transfer article's explanations."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/proximal-distal-energy-transfer.qmd"
BIBLIOGRAPHY = ROOT / "articles/proximal-distal-energy-transfer-bibliography.md"


def unit(angle: float) -> np.ndarray:
    return np.array([np.sin(angle), -np.cos(angle)])


def tangent(angle: float) -> np.ndarray:
    return np.array([np.cos(angle), np.sin(angle)])


def mass_from_jacobians(q: np.ndarray) -> np.ndarray:
    """Two unit uniform rods, with unit mass and length."""
    arm_j = np.column_stack([0.5 * tangent(q[0]), np.zeros(2)])
    club_j = np.column_stack([tangent(q[0]) + 0.5 * tangent(q.sum()), 0.5 * tangent(q.sum())])
    return arm_j.T @ arm_j + club_j.T @ club_j + np.diag([1 / 12, 0]) + np.ones((2, 2)) / 12


def inertial_bias(q: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    """Obtain the quadratic term from numerical derivatives of the mass matrix."""
    step = 1e-5
    derivatives = np.array(
        [
            (
                mass_from_jacobians(q + step * np.eye(2)[k])
                - mass_from_jacobians(q - step * np.eye(2)[k])
            )
            / (2 * step)
            for k in range(2)
        ]
    )
    return np.array(
        [
            sum(
                0.5
                * (derivatives[k, i, j] + derivatives[j, i, k] - derivatives[i, j, k])
                * velocity[j]
                * velocity[k]
                for j in range(2)
                for k in range(2)
            )
            for i in range(2)
        ]
    )


def club_ledger(
    q: np.ndarray, velocity: np.ndarray, acceleration: np.ndarray, gravity: float = 0.0
) -> tuple[float, float, float]:
    """Return force power, rotational kinetic power, and total mechanical power."""
    hand_velocity = velocity[0] * tangent(q[0])
    com_velocity = hand_velocity + 0.5 * velocity.sum() * tangent(q.sum())
    com_acceleration = (
        acceleration[0] * tangent(q[0])
        - velocity[0] ** 2 * unit(q[0])
        + 0.5 * acceleration.sum() * tangent(q.sum())
        - 0.5 * velocity.sum() ** 2 * unit(q.sum())
    )
    force = com_acceleration + np.array([0, gravity])
    rotational_power = velocity.sum() * acceleration.sum() / 12
    energy_rate = com_velocity @ com_acceleration + rotational_power + gravity * com_velocity[1]
    return float(force @ hand_velocity), float(rotational_power), float(energy_rate)


def test_mass_matrix_has_com_parallel_axis_and_cross_terms() -> None:
    for q in [np.array([0.2, 0.7]), np.array([-0.4, -1.8]), np.array([0.0, np.pi])]:
        cosine = np.cos(q[1])
        expected = [[5 / 3 + cosine, 1 / 3 + cosine / 2], [1 / 3 + cosine / 2, 1 / 3]]
        np.testing.assert_allclose(mass_from_jacobians(q), expected, atol=1e-14)
        assert np.linalg.eigvalsh(mass_from_jacobians(q)).min() > 0


def test_bias_vector_is_not_a_coriolis_matrix_entry_times_speed_squared() -> None:
    q, v = np.array([0.4, -0.8]), np.array([2.0, -1.2])
    expected = 0.5 * np.sin(q[1]) * np.array([-(2 * v[0] * v[1] + v[1] ** 2), v[0] ** 2])
    np.testing.assert_allclose(inertial_bias(q, v), expected, atol=1e-9)


def test_inertial_interaction_sign_is_geometry_dependent() -> None:
    assert mass_from_jacobians(np.array([0.0, 0.0]))[1, 0] == pytest.approx(5 / 6)
    assert mass_from_jacobians(np.array([0.0, np.pi]))[1, 0] == pytest.approx(-1 / 6)


def test_arm_deceleration_and_club_angular_acceleration_can_lose_club_energy() -> None:
    q, v = np.zeros(2), np.array([2.0, 0.0])
    acceleration = np.linalg.solve(mass_from_jacobians(q), [-1.0, 0.0])
    np.testing.assert_allclose(acceleration, [-12 / 7, 30 / 7])
    force_power, rotational_power, club_power = club_ledger(q, v, acceleration)
    assert acceleration[0] < 0 < acceleration.sum()
    assert force_power == pytest.approx(-6 / 7)
    assert rotational_power == pytest.approx(3 / 7)
    assert club_power == pytest.approx(-6 / 7)
    arm_power = v[0] * acceleration[0] / 3
    assert arm_power + club_power == pytest.approx(-2)


def test_a_passive_chain_can_transfer_energy_without_net_work() -> None:
    q, v = np.array([0.0, -np.pi / 2]), np.array([2.0, 0.0])
    acceleration = np.linalg.solve(mass_from_jacobians(q), -inertial_bias(q, v))
    np.testing.assert_allclose(acceleration, [-1.5, 7.5], atol=1e-8)
    force_power, _, club_power = club_ledger(q, v, acceleration)
    arm_power = v[0] * acceleration[0] / 3
    assert force_power == pytest.approx(1.0)
    assert club_power == pytest.approx(1.0)
    assert arm_power == pytest.approx(-1.0)


def test_complete_segment_ledgers_close_with_gravity_and_joint_damping() -> None:
    q, v = np.array([0.4, -0.8]), np.array([2.0, -1.2])
    gravity, shoulder, wrist, b1, b2 = 7.0, 3.0, 0.6, 0.1, 0.2
    potential_gradient = gravity * np.array(
        [1.5 * np.sin(q[0]) + 0.5 * np.sin(q.sum()), 0.5 * np.sin(q.sum())]
    )
    net = np.array([shoulder - b1 * v[0], wrist - b2 * v[1]])
    acceleration = np.linalg.solve(
        mass_from_jacobians(q), net - inertial_bias(q, v) - potential_gradient
    )
    force_power, _, club_power = club_ledger(q, v, acceleration, gravity)
    assert club_power == pytest.approx(force_power + net[1] * v.sum(), abs=2e-9)
    arm_power = v[0] * acceleration[0] / 3 + 0.5 * gravity * np.sin(q[0]) * v[0]
    assert arm_power == pytest.approx(net[0] * v[0] - force_power - net[1] * v[0])
    assert arm_power + club_power == pytest.approx(net @ v, abs=2e-9)


def test_club_side_moment_power_and_actuator_power_are_different() -> None:
    omega_arm, omega_club, moment = 2.0, 5.0, 3.0
    assert moment * omega_club == 15
    assert moment * (omega_club - omega_arm) == 9
    assert moment * omega_club - moment * omega_arm == 9
    assert moment * (omega_arm - omega_arm) == 0


def test_alignment_maximizes_speed_only_for_agreeing_absolute_rates() -> None:
    arm_rate, relative_rate = 2.0, -3.0
    aligned = arm_rate * tangent(0) + (arm_rate + relative_rate) * tangent(0)
    folded = arm_rate * tangent(0) + (arm_rate + relative_rate) * tangent(np.pi)
    assert np.linalg.norm(aligned) == pytest.approx(1)
    assert np.linalg.norm(folded) == pytest.approx(3)


def test_pure_hand_path_normal_force_does_no_work_but_inward_motion_can() -> None:
    force = np.array([-400.0, 0])
    assert force @ np.array([0.0, 3.0]) == 0
    assert force @ np.array([-0.2, 3.0]) == 80
    assert force @ np.array([0.2, 3.0]) == -80


def test_point_transport_preserves_total_power_but_not_its_split() -> None:
    force, omega = np.array([0.0, 2.0, 0.0]), np.array([0.0, 0.0, 3.0])
    displacement = np.array([1.0, 0.0, 0.0])
    va, ma = np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 4.0])
    vb, mb = va + np.cross(omega, displacement), ma - np.cross(displacement, force)
    assert force @ va == 2
    assert force @ vb == 8
    assert force @ va + ma @ omega == force @ vb + mb @ omega == 14


def test_observer_boost_changes_power_consistently() -> None:
    force, velocity, observer = np.array([2.0, 1.0]), np.array([3.0, -1.0]), np.array([4.0, 0])
    assert force @ velocity == 5
    assert force @ (velocity - observer) == -3
    assert force @ (velocity - observer) == force @ velocity - force @ observer


def test_absolute_coordinate_torques_are_not_relative_coordinate_torques() -> None:
    absolute_to_relative = np.array([[1.0, 0.0], [-1.0, 1.0]])
    relative_torques, absolute_rates = np.array([7.0, 3.0]), np.array([2.0, 5.0])
    absolute_torques = absolute_to_relative.T @ relative_torques
    np.testing.assert_array_equal(absolute_torques, [4, 3])
    assert absolute_torques @ absolute_rates == relative_torques @ (
        absolute_to_relative @ absolute_rates
    )


def test_path_average_force_is_not_time_average_force() -> None:
    force, speed = np.array([1.0, 3.0]), np.array([1.0, 3.0])
    assert np.mean(force) == 2
    assert force @ speed / np.sum(speed) == 2.5


def test_symmetric_relative_error_is_not_a_work_ratio() -> None:
    left, right = 30.0, 2.0
    symmetric_error = abs(left - right) / (0.5 * (abs(left) + abs(right)))
    assert symmetric_error == 1.75
    assert left / right == 15
    assert (2 + symmetric_error) / (2 - symmetric_error) == 15


def test_contact_power_for_compliance_includes_elastic_storage() -> None:
    stiffness, damping, extension, rate = 100.0, 2.0, 0.01, -0.2
    attachment_power = -(stiffness * extension + damping * rate) * rate
    storage_rate = stiffness * extension * rate
    assert attachment_power > 0
    assert attachment_power + storage_rate == pytest.approx(-damping * rate**2)


@pytest.mark.parametrize(
    "required",
    [
        "Club-Side Power and Joint-Actuator Power",
        "An Acceleration Counterexample",
        "Changing the Observer Changes Mechanical Power",
        "symmetric relative difference",
    ],
)
def test_article_explains_the_identified_mechanical_distinctions(required: str) -> None:
    assert required in ARTICLE.read_text(encoding="utf-8")


def test_bibliography_does_not_define_casting_as_an_inevitable_failure() -> None:
    text = BIBLIOGRAPHY.read_text(encoding="utf-8")
    assert "Casting Failure Mode" not in text
    assert "McCourt, Matthew" in text
    assert "Champoux, Luc" in text
