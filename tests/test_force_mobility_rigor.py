"""Independent mechanics and executable-example checks for force/mobility."""

import ast
import re
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose

SOURCE = Path(__file__).resolve().parents[1] / "articles/force-mobility-matrices.qmd"


def _published_axes(matrix: np.ndarray, **kwargs: float) -> tuple:
    """Execute only the article's named demonstration, not arbitrary fenced code."""
    blocks = re.findall(r"```python\n(.*?)```", SOURCE.read_text(encoding="utf-8"), re.S)
    for block in blocks:
        for node in ast.parse(block).body:
            if isinstance(node, ast.FunctionDef) and node.name == "ellipsoid_axes":
                namespace = {"np": np}
                module = ast.Module(body=[node], type_ignores=[])
                exec(compile(module, str(SOURCE), "exec"), namespace)
                return namespace["ellipsoid_axes"](matrix, **kwargs)
    raise AssertionError("The published ellipsoid_axes demonstration is missing")


@pytest.mark.parametrize("shape", [(3, 2), (2, 3), (2, 2)])
def test_example_represents_every_task_null_direction(shape: tuple[int, int]) -> None:
    matrix = np.zeros(shape)
    matrix[0, 0] = 2
    axes, _, mobility, force = _published_axes(matrix)
    assert axes.shape == (shape[0], shape[0])
    assert_allclose(axes.T @ axes, np.eye(shape[0]))
    assert_allclose(mobility, [2] + [0] * (shape[0] - 1))
    assert force[0] == pytest.approx(0.5)
    assert np.all(np.isinf(force[1:]))
    assert_allclose(matrix.T @ axes[:, 1:], 0, atol=1e-14)


def test_numerical_rank_threshold_is_scale_relative_and_disclosed() -> None:
    matrix = np.diag([2.0, 1e-12])
    for scale in [1e-6, 1, 1e6]:
        _, raw, mobility, force = _published_axes(scale * matrix, rtol=1e-10)
        assert raw[1] > 0  # Physical near-singularity differs from numerical truncation.
        assert mobility[1] == 0 and np.isinf(force[1])
        assert mobility[0] * force[0] == pytest.approx(1)


@pytest.mark.parametrize("bad", [np.array([1, 2]), np.array([[np.nan]]), np.empty((0, 2))])
def test_example_rejects_undefined_input_metrics(bad: np.ndarray) -> None:
    with pytest.raises(ValueError):
        _published_axes(bad)


def test_zero_map_has_zero_mobility_and_unbounded_force_preimage() -> None:
    axes, _, mobility, force = _published_axes(np.zeros((3, 2)))
    assert axes.shape == (3, 3)
    assert_allclose(mobility, 0)
    assert np.isinf(force).all()


def test_weighted_velocity_support_and_polar_pairing() -> None:
    jacobian = np.array([[2.0, 1.0], [0.0, 1.0]])
    weight = np.diag([4.0, 1.0])
    shape = jacobian @ np.linalg.solve(weight, jacobian.T)
    direction = np.array([1.0, -0.5])
    support = np.sqrt(direction @ shape @ direction)
    rate = np.linalg.solve(weight, jacobian.T @ direction) / support
    force = direction / support
    assert rate @ weight @ rate == pytest.approx(1)
    assert force @ shape @ force == pytest.approx(1)
    assert force @ jacobian @ rate == pytest.approx(1)


def test_independent_torque_limits_destroy_reciprocal_semiaxes() -> None:
    jacobian = np.diag([2.0, 1.0])
    velocity_axes = np.linalg.svd(jacobian, compute_uv=False)
    torque_weight = np.diag([0.01, 1.0])
    force_shape = jacobian @ torque_weight @ jacobian.T
    force_x_radius = 1 / np.sqrt(force_shape[0, 0])
    assert force_x_radius == pytest.approx(5)
    assert force_x_radius != pytest.approx(1 / velocity_axes[0])


def test_power_pairing_survives_coordinate_rescaling_with_dual_force() -> None:
    jacobian = np.array([[2.0, 1.0], [1.0, -1.0]])
    rates, force = np.array([0.2, -0.3]), np.array([4.0, 2.0])
    transform = np.diag([1000.0, 1.0])
    task_velocity = jacobian @ rates
    new_force = np.linalg.solve(transform.T, force)
    assert new_force @ transform @ task_velocity == pytest.approx(force @ task_velocity)
    assert_allclose((transform @ jacobian).T @ new_force, jacobian.T @ force)


def test_extended_two_link_arm_has_axial_second_order_motion() -> None:
    jacobian = np.array([[0.0, 0.0], [2.0, 1.0]])
    axial_force = np.array([1000.0, 0.0])
    assert_allclose(jacobian.T @ axial_force, 0)
    step = 1e-4
    center = np.array([2.0, 0.0])
    plus = 2 * np.array([np.cos(step), np.sin(step)])
    minus = 2 * np.array([np.cos(-step), np.sin(-step)])
    assert_allclose((plus - 2 * center + minus) / step**2, [-2.0, 0], atol=1e-7)


def test_high_kinematic_gain_can_have_small_acceleration_gain() -> None:
    jacobian, mass = np.diag([2.0, 1.0]), np.diag([100.0, 0.25])
    acceleration_map = np.linalg.solve(mass, jacobian.T).T
    assert_allclose(np.diag(acceleration_map), [0.02, 4])
    assert jacobian[0, 0] > jacobian[1, 1]
    assert acceleration_map[0, 0] < acceleration_map[1, 1]


def test_joint_stiffness_changes_compliance_without_changing_force_ellipsoid() -> None:
    jacobian = np.diag([2.0, 1.0])
    first = jacobian @ np.linalg.solve(np.diag([4.0, 1.0]), jacobian.T)
    second = jacobian @ np.linalg.solve(np.diag([16.0, 1.0]), jacobian.T)
    assert_allclose(np.diag(first), [1, 1])
    assert_allclose(np.diag(second), [0.25, 1])
    _, _, _, force_axes = _published_axes(jacobian)
    assert_allclose(force_axes, [0.5, 1])


def test_grasp_internal_force_and_constraint_reaction_use_different_maps() -> None:
    grasp = np.array([[1.0, 1.0]])
    internal = np.array([3.0, -3.0])
    assert_allclose(grasp @ internal, 0)
    constraint = np.array([[1.0, -1.0]])
    allowable_rate = np.array([2.0, 2.0])
    assert_allclose(constraint @ allowable_rate, 0)
    assert allowable_rate @ constraint.T @ [3.0] == pytest.approx(0)
    assert np.linalg.matrix_rank(constraint) == 1  # Closure is not automatically redundancy.


def test_static_bias_changes_the_available_force_set() -> None:
    jacobian, bias, bound = 2.0, 1.0, 3.0
    endpoints = (np.array([-bound, bound]) - bias) / jacobian
    assert_allclose(endpoints, [-2, 1])
    assert not np.allclose(endpoints, [-bound / jacobian, bound / jacobian])


def test_loaded_spring_includes_geometric_stiffness() -> None:
    # x=q^2, actuator spring gradient k(q-q0); load potential is -F*x(q).
    stiffness, load = 10.0, 3.0
    step = 1e-3

    def potential(coordinate: float) -> float:
        return 0.5 * stiffness * coordinate**2 - load * coordinate**2

    tangent = (potential(step) - 2 * potential(0) + potential(-step)) / step**2
    assert tangent == pytest.approx(stiffness - 2 * load)
    assert tangent != stiffness


def test_two_link_numbers_match_a_finite_difference_jacobian() -> None:
    def endpoint(angles: np.ndarray) -> np.ndarray:
        absolute = np.cumsum(angles)
        return np.array([np.cos(absolute).sum(), np.sin(absolute).sum()])

    angles, step = np.array([0.3, 1.2]), 1e-5
    jacobian = np.column_stack(
        [
            (endpoint(angles + delta) - endpoint(angles - delta)) / (2 * step)
            for delta in step * np.eye(2)
        ]
    )
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    assert_allclose(singular_values, [1.86405738, 0.50000558], atol=1e-8)
    assert_allclose(1 / singular_values, [0.53646417, 1.9999777], atol=1e-8)


def test_pseudoinverse_inequality_alone_admits_impossible_velocity() -> None:
    shape = np.diag([4.0, 0.0])
    velocity = np.array([0.0, 10.0])
    assert velocity @ np.linalg.pinv(shape) @ velocity == 0
    assert not np.allclose(shape @ np.linalg.pinv(shape) @ velocity, velocity)


def test_constrained_response_matches_augmented_impulse_equations() -> None:
    mass, constraint = np.diag([2.0, 3.0]), np.array([[1.0, -1.0]])
    inverse = np.linalg.inv(mass)
    response = inverse - inverse @ constraint.T @ np.linalg.solve(
        constraint @ inverse @ constraint.T, constraint @ inverse
    )
    impulse = np.array([1.0, 0.0])
    augmented = np.block([[mass, -constraint.T], [constraint, np.zeros((1, 1))]])
    solution = np.linalg.solve(augmented, np.r_[impulse, 0])
    assert_allclose(response @ impulse, solution[:2])
    assert_allclose(constraint @ response, 0, atol=1e-15)
    assert 1 / response[0, 0] == pytest.approx(5)
    assert 1 / inverse[0, 0] == pytest.approx(2)
