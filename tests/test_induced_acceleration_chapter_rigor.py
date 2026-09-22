"""Independent output, coupling and history checks for the IAA chapter."""

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp


def test_equal_torque_reciprocity_differs_from_normalized_coupling() -> None:
    mass = np.array([[8 / 3, 5 / 6], [5 / 6, 1 / 3]])
    mobility = np.linalg.solve(mass, np.eye(2))
    first = np.linalg.solve(mass, [1, 0])
    second = np.linalg.solve(mass, [0, 1])
    assert first[1] == pytest.approx(second[0])
    assert mobility == pytest.approx(mobility.T)
    assert abs(first[1] / first[0]) == pytest.approx(2.5)
    assert abs(second[0] / second[1]) == pytest.approx(0.3125)
    assert abs(first[1] / first[0]) == pytest.approx(abs(mass[1, 0] / mass[1, 1]))


def test_linked_uniform_rods_can_have_zero_cross_acceleration() -> None:
    elbow = np.arccos(-2 / 3)
    mass = np.array(
        [[5 / 3 + np.cos(elbow), 1 / 3 + np.cos(elbow) / 2], [1 / 3 + np.cos(elbow) / 2, 1 / 3]]
    )
    acceleration = np.linalg.solve(mass, [1, 0])
    assert np.all(np.linalg.eigvalsh(mass) > 0)
    assert acceleration == pytest.approx([1, 0], abs=1e-14)


def test_multiple_passive_coordinates_require_a_block_solve() -> None:
    mass = np.array([[3, 1, 0.5], [1, 2, 0.6], [0.5, 0.6, 1]])
    acceleration = np.linalg.solve(mass, [1, 0, 0])
    normalized = acceleration[1:] / acceleration[0]
    block_answer = -np.linalg.solve(mass[1:, 1:], mass[1:, 0])
    assert normalized == pytest.approx(block_answer)
    assert not np.allclose(normalized, -mass[1:, 0] / np.diag(mass)[1:])


def test_physical_output_increment_survives_coordinate_rescaling() -> None:
    mass = np.array([[3, 1], [1, 2]])
    transform = np.array([[2.0, 0.4], [0, 0.5]])
    force, output = np.array([4, -1]), np.array([[0.5, 2.0]])
    original = np.linalg.solve(mass, force)
    transformed = np.linalg.solve(transform.T @ mass @ transform, transform.T @ force)
    assert not np.allclose(original, transformed)
    assert transform @ transformed == pytest.approx(original)
    assert output @ transform @ transformed == pytest.approx(output @ original)


def test_nonlinear_coordinates_need_the_acceleration_transport_term() -> None:
    # A free particle q=z^2 has q_ddot=0 even though z_ddot is nonzero.
    coordinate, speed = 2.0, 3.0
    acceleration = -(speed**2) / coordinate
    assert 2 * coordinate * acceleration + 2 * speed**2 == pytest.approx(0)
    assert acceleration != 0


def test_rotating_point_accelerates_without_joint_angular_acceleration() -> None:
    angle, speed, length = 0.4, 3.0, 0.8
    position = length * np.array([np.cos(angle), np.sin(angle)])
    time_step = 1e-4
    before = length * np.array(
        [np.cos(angle - speed * time_step), np.sin(angle - speed * time_step)]
    )
    after = length * np.array(
        [np.cos(angle + speed * time_step), np.sin(angle + speed * time_step)]
    )
    numerical_acceleration = (after - 2 * position + before) / time_step**2
    assert numerical_acceleration == pytest.approx(-(speed**2) * position, rel=1e-7)
    assert np.linalg.norm(numerical_acceleration) > 0


def test_distinct_input_histories_reach_the_same_position_and_velocity() -> None:
    def ordinary(_time: float, state: np.ndarray) -> list[float]:
        return [state[1], 1.0]

    def changed(time: float, state: np.ndarray) -> list[float]:
        return [state[1], 2 + 6 * time**2 - 6 * time]

    first = solve_ivp(ordinary, (0, 1), [0, 0], rtol=1e-11, atol=1e-12)
    second = solve_ivp(changed, (0, 1), [0, 0], rtol=1e-11, atol=1e-12)
    assert second.y[:, -1] == pytest.approx(first.y[:, -1])
    assert first.y[:, -1] == pytest.approx([0.5, 1])


def test_integrated_nominal_terms_are_not_removed_input_trajectories() -> None:
    final_time = 0.5
    solution = solve_ivp(lambda _t, state: state**2 + 1, (0, final_time), [0], rtol=1e-11)
    endpoint = solution.y[0, -1]
    nominal_input_term = final_time
    nominal_state_term = quad(lambda time: np.tan(time) ** 2, 0, final_time)[0]
    assert endpoint == pytest.approx(np.tan(final_time), rel=1e-6)
    assert endpoint == pytest.approx(nominal_input_term + nominal_state_term, rel=1e-6)
    removed_input_endpoint = 0.0
    assert endpoint - removed_input_endpoint != pytest.approx(nominal_input_term)
