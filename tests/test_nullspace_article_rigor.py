"""Independent mechanics controls for the null-space article review (#4371)."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm, null_space

from scripts.build_nullspace_examples import (
    closed_chain,
    constraint_solve,
    make_examples,
    rotation_frame,
    spring_system,
)


def test_anisotropic_projection_matches_direct_saddle_system() -> None:
    mass, jacobian = np.array([[2.0, 1.0], [1.0, 3.0]]), np.array([[1.0, 1.0]])
    force = np.array([1.0, 0.0])
    result = make_examples()["anisotropic"]
    saddle = np.block([[mass, -jacobian.T], [jacobian, np.zeros((1, 1))]])
    reference = np.linalg.solve(saddle, [1.0, 0.0, 0.0])
    np.testing.assert_allclose(result["acceleration"], reference[:2], atol=1e-14)
    np.testing.assert_allclose(result["reaction"], reference[2:], atol=1e-14)
    euclidean = np.eye(2) - jacobian.T @ np.linalg.solve(jacobian @ jacobian.T, jacobian)
    wrong = np.linalg.solve(mass, euclidean @ force)
    assert float((jacobian @ wrong)[0]) == pytest.approx(0.1)


def test_force_velocity_projectors_are_dual_and_mass_orthogonal() -> None:
    result = make_examples()["anisotropic"]
    force_map, velocity_map = np.array(result["force_projector"]), np.array(
        result["velocity_projector"]
    )
    mass = np.array([[2.0, 1.0], [1.0, 3.0]])
    np.testing.assert_allclose(force_map.T, velocity_map, atol=1e-14)
    np.testing.assert_allclose(velocity_map @ velocity_map, velocity_map, atol=1e-14)
    np.testing.assert_allclose(velocity_map.T @ mass, mass @ velocity_map, atol=1e-14)
    np.testing.assert_allclose(force_map @ [1, 1], 0, atol=1e-14)
    assert not np.allclose(force_map, force_map.T)
    tangent = np.array([[1.0], [-1.0]])  # Deliberately not normalized.
    reduced = tangent @ np.linalg.solve(tangent.T @ mass @ tangent, tangent.T)
    np.testing.assert_allclose(result["force_to_acceleration"], reduced, atol=1e-14)


def test_circle_curvature_and_power_match_analytic_trajectory() -> None:
    result = make_examples()["circle"]
    # q=(1,0), qdot=(0,3), phi=(q.q-1)/2; phi_ddot=q.a+v.v.
    acceleration = np.array(result["acceleration"])
    np.testing.assert_allclose(acceleration, [-9, -9.81], atol=1e-13)
    assert acceleration[0] + 9 == pytest.approx(0)
    np.testing.assert_allclose(result["reaction"], [-18], atol=1e-13)
    assert result["reaction_power"] == pytest.approx(0)
    tangent = np.array([[0.0], [1.0]])
    tangent_rate = np.array([[-3.0], [0.0]])
    reconstructed = tangent[:, 0] * -9.81 + tangent_rate[:, 0] * 3
    np.testing.assert_allclose(acceleration, reconstructed, atol=1e-13)


def test_moving_guide_reaction_has_nonzero_physical_power() -> None:
    result = make_examples()["moving_guide"]
    # Two-kg mass, x=t^2 at t=1: a=2, v=2, applied force=3 N.
    np.testing.assert_allclose(result["acceleration"], [2])
    np.testing.assert_allclose(result["reaction"], [1])
    assert result["reaction_power"] == pytest.approx(2)
    assert result["kinetic_power"] == pytest.approx(8)
    assert result["applied_power"] + result["reaction_power"] == pytest.approx(8)


def test_rescaling_constraints_preserves_motion_and_physical_reaction() -> None:
    mass, force, jacobian = [[2, 1], [1, 3]], [1, -2], np.array([[1.0, 1.0]])
    base_a, base_lambda = constraint_solve(mass, force, jacobian, [0.7])
    scaled_a, scaled_lambda = constraint_solve(mass, force, -1000 * jacobian, [-700])
    np.testing.assert_allclose(base_a, scaled_a, atol=1e-12)
    np.testing.assert_allclose(jacobian.T @ base_lambda, -1000 * jacobian.T @ scaled_lambda)


def test_orthonormal_tangent_frame_need_not_be_a_coordinate_frame() -> None:
    point, step = np.array([0.4, 0.2, 0.0]), 1e-6
    frame = rotation_frame(point)
    np.testing.assert_allclose(frame.T @ frame, np.eye(2), atol=1e-14)
    np.testing.assert_allclose(np.array([[0, 0, 1]]) @ frame, 0)
    derivative_second = (
        rotation_frame(point + step * frame[:, 0])[:, 1]
        - rotation_frame(point - step * frame[:, 0])[:, 1]
    ) / (2 * step)
    derivative_first = (
        rotation_frame(point + step * frame[:, 1])[:, 0]
        - rotation_frame(point - step * frame[:, 1])[:, 0]
    ) / (2 * step)
    np.testing.assert_allclose(derivative_second - derivative_first, [-1, 0, 0], atol=1e-10)


def test_single_input_spring_pair_is_controllable_over_time() -> None:
    state_matrix, input_matrix = spring_system()
    controllability = np.column_stack(
        [np.linalg.matrix_power(state_matrix, power) @ input_matrix for power in range(4)]
    )
    assert np.linalg.matrix_rank(input_matrix[2:]) == 1
    assert np.linalg.matrix_rank(controllability) == 4
    assert abs(np.linalg.det(controllability)) == pytest.approx(1)
    np.testing.assert_allclose(make_examples()["springs"]["controllability"], controllability)


def test_minimum_energy_input_actually_reaches_the_specified_state() -> None:
    state_matrix, input_matrix = spring_system()
    result = make_examples()["springs"]
    horizon = result["horizon"]
    terminal = np.array([0.0, 1.0, 0.0, 0.0])
    multiplier = np.linalg.solve(result["gramian"], terminal)

    def dynamics(time: float, state: np.ndarray) -> np.ndarray:
        control = float((input_matrix.T @ expm(state_matrix.T * (horizon - time)) @ multiplier)[0])
        return np.r_[state_matrix @ state[:4] + input_matrix[:, 0] * control, control**2]

    solution = solve_ivp(dynamics, [0, horizon], np.zeros(5), rtol=1e-10, atol=1e-11)
    assert solution.success
    np.testing.assert_allclose(solution.y[:4, -1], terminal, atol=1e-8)
    assert solution.y[4, -1] == pytest.approx(result["minimum_energy"], rel=1e-8)


def test_planar_grasp_closes_and_includes_rotating_grip_offsets() -> None:
    configuration = np.array(make_examples()["planar_grasp"]["configuration"])
    closure, jacobian, _ = closed_chain(configuration)
    np.testing.assert_allclose(closure, 0, atol=1e-13)
    assert jacobian.shape == (4, 7)
    assert np.linalg.matrix_rank(jacobian) == 4
    step = 1e-6
    numerical = np.column_stack(
        [
            (
                closed_chain(configuration + direction * step)[0]
                - closed_chain(configuration - direction * step)[0]
            )
            / (2 * step)
            for direction in np.eye(7)
        ]
    )
    np.testing.assert_allclose(jacobian, numerical, atol=1e-9)
    assert np.linalg.norm(jacobian[:, -1]) > 0.1


def test_admissible_motion_can_leave_club_point_velocity_zero() -> None:
    configuration = np.array(make_examples()["planar_grasp"]["configuration"])
    _, jacobian, task_map = closed_chain(configuration)
    stationary_point_direction = null_space(np.vstack([jacobian, task_map]))
    assert stationary_point_direction.shape == (7, 1)
    np.testing.assert_allclose(jacobian @ stationary_point_direction, 0, atol=1e-14)
    np.testing.assert_allclose(task_map @ stationary_point_direction, 0, atol=1e-14)
    assert abs(stationary_point_direction[-1, 0]) > 0.1


def test_redundant_basis_rotation_cannot_identify_physiological_synergies() -> None:
    frame = rotation_frame(np.array([0.4, 0.2, 0.0]))
    rotation = np.array([[0.6, -0.8], [0.8, 0.6]])
    changed = frame @ rotation
    assert not np.allclose(frame, changed)
    np.testing.assert_allclose(frame @ frame.T, changed @ changed.T, atol=1e-14)
    np.testing.assert_allclose(np.linalg.eigvalsh(frame @ frame.T), [0, 1, 1], atol=1e-14)


def test_rotating_point_needs_the_changing_jacobian_acceleration() -> None:
    step, angle, speed, radius = 1e-4, np.pi / 4, 2.0, 0.5

    def point(time: float) -> np.ndarray:
        return radius * np.array([np.cos(angle + speed * time), np.sin(angle + speed * time)])

    numerical = (point(step) - 2 * point(0) + point(-step)) / step**2
    np.testing.assert_allclose(numerical, -(speed**2) * point(0), atol=1e-7)
    assert np.linalg.norm(numerical) == pytest.approx(2)


@pytest.mark.parametrize("mass", [[[1, 2], [0, 1]], [[1, 0], [0, -1]], [[np.nan, 0], [0, 1]]])
def test_constraint_solver_rejects_invalid_mass_metric(mass: list[list[float]]) -> None:
    with pytest.raises(ValueError):
        constraint_solve(mass, [0, 0], [[1, 1]], [0])


def test_saved_examples_reproduce_without_claiming_empirical_validation() -> None:
    path = Path(__file__).resolve().parents[1] / "reports/technical-review/nullspace-examples.json"
    saved, generated = json.loads(path.read_text()), make_examples()
    assert saved["scope"] == generated["scope"] == "Constructed examples; no fitted golfer data"
    for group in ["anisotropic", "circle", "moving_guide", "springs", "planar_grasp"]:
        assert saved[group].keys() == generated[group].keys()
        for key, value in generated[group].items():
            np.testing.assert_allclose(saved[group][key], value, rtol=1e-11, atol=1e-12)
