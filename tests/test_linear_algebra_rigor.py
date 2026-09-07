"""Independent counterexamples for the linear-algebra chapter's physical claims."""

from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "articles/The_Geometry_of_Motion/Volume_0/chapters/ch01_linear_algebra.tex"
WEB = ROOT / "articles/The_Geometry_of_Motion/quarto/vol0_ch01_linear_algebra.qmd"
GRAVITY_M_S2 = 9.81


def test_orientation_reversal_does_not_preserve_volume_magnitude() -> None:
    transform = np.diag([-2.0, 3.0])
    assert np.linalg.det(transform) == pytest.approx(-6)
    assert np.prod(np.linalg.svd(transform, compute_uv=False)) == pytest.approx(6)


def test_scalar_and_vector_projections_have_different_types_and_values() -> None:
    direction, vector = np.array([2.0, 0.0]), np.array([3.0, 4.0])
    scalar = direction @ vector / np.linalg.norm(direction)
    projection = direction * (direction @ vector) / (direction @ direction)
    assert scalar == 3
    np.testing.assert_array_equal(projection, [3, 0])
    assert direction @ (vector - projection) == 0


def test_shear_ellipse_axes_are_singular_vectors_not_eigenvectors() -> None:
    shear = np.array([[1.0, 1.0], [0.0, 1.0]])
    left, values, right_t = np.linalg.svd(shear)
    np.testing.assert_array_equal(np.linalg.eigvals(shear), [1, 1])
    np.testing.assert_allclose(values, [(1 + np.sqrt(5)) / 2, (np.sqrt(5) - 1) / 2])
    np.testing.assert_allclose(shear @ right_t.T[:, 0], values[0] * left[:, 0])
    assert not np.allclose(shear @ left[:, 0], left[:, 0])


def test_negative_symmetric_eigenvalues_give_positive_semiaxis_lengths() -> None:
    transform = np.diag([3.0, -2.0])
    np.testing.assert_array_equal(np.linalg.eigvalsh(transform), [-2, 3])
    np.testing.assert_allclose(np.linalg.svd(transform, compute_uv=False), [3, 2])


def test_planar_quarter_turn_has_no_real_eigenvector() -> None:
    rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    values, vectors = np.linalg.eig(rotation)
    assert np.all(np.abs(values.imag) == 1)
    np.testing.assert_allclose(rotation @ vectors, vectors @ np.diag(values))


def test_zero_eigenvalues_do_not_distinguish_bounded_from_unbounded_linear_motion() -> None:
    jordan = np.array([[0.0, 1.0], [0.0, 0.0]])
    initial = np.array([0.0, 1.0])
    np.testing.assert_array_equal(np.linalg.eigvals(jordan), [0, 0])
    np.testing.assert_allclose(expm(10 * jordan) @ initial, [10, 1])
    np.testing.assert_array_equal(expm(np.zeros((2, 2))) @ initial, initial)


def test_hurwitz_eigenvalues_allow_transient_norm_growth() -> None:
    dynamics = np.array([[-1.0, 10.0], [0.0, -1.0]])
    initial = np.array([0.0, 1.0])
    np.testing.assert_array_equal(np.linalg.eigvals(dynamics), [-1, -1])
    state = expm(dynamics) @ initial
    np.testing.assert_allclose(state, np.exp(-1) * np.array([10, 1]))
    assert np.linalg.norm(state) > 3.6 * np.linalg.norm(initial)
    assert np.linalg.norm(expm(20 * dynamics) @ initial) < 1e-6


def test_nonincreasing_quadratic_energy_does_not_imply_convergence() -> None:
    rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    state = np.array([2.0, 1.0])
    assert state @ (rotation + rotation.T) @ state == 0
    assert np.linalg.norm(expm(10 * rotation) @ state) == pytest.approx(np.linalg.norm(state))


def test_task_redundancy_does_not_require_rank_loss() -> None:
    jacobian = np.column_stack([np.eye(3), np.ones((3, 4))])
    assert np.linalg.matrix_rank(jacobian) == 3
    null_projector = np.eye(7) - np.linalg.pinv(jacobian) @ jacobian
    assert np.linalg.matrix_rank(null_projector, tol=1e-10) == 4
    np.testing.assert_allclose(jacobian @ null_projector, 0, atol=1e-14)


def test_initial_task_null_velocity_does_not_preserve_finite_position() -> None:
    initial_jacobian = np.array([[0.0, 0.0], [2.0, 1.0]])
    direction = np.array([1.0, -2.0])
    np.testing.assert_array_equal(initial_jacobian @ direction, [0, 0])
    angles = 0.1 * direction
    tip = np.array(
        [np.cos(angles[0]) + np.cos(angles.sum()), np.sin(angles[0]) + np.sin(angles.sum())]
    )
    np.testing.assert_allclose(tip, [2 * np.cos(0.1), 0], atol=1e-14)
    assert tip[0] < 2


def test_rank_one_input_can_control_two_dynamic_states() -> None:
    dynamics = np.array([[0.0, 1.0], [0.0, 0.0]])
    input_map = np.array([[0.0], [1.0]])
    assert np.linalg.matrix_rank(input_map) == 1
    assert np.linalg.matrix_rank(np.column_stack([input_map, dynamics @ input_map])) == 2
    horizon = 2.0
    gramian = np.array([[horizon**3 / 3, horizon**2 / 2], [horizon**2 / 2, horizon]])
    assert np.linalg.det(gramian) == pytest.approx(horizon**4 / 12)


def test_condition_one_does_not_bound_absolute_inverse_gain() -> None:
    jacobian = 1e-3 * np.eye(2)
    assert np.linalg.cond(jacobian) == 1
    assert np.linalg.norm(np.linalg.pinv(jacobian), 2) == 1000


def test_pseudoinverse_retains_small_singular_value_amplification() -> None:
    jacobian = np.diag([1.0, 1e-3])
    command = np.linalg.pinv(jacobian) @ [1.0, 1.0]
    np.testing.assert_array_equal(command, [1, 1000])
    error = np.linalg.pinv(jacobian) @ [0.0, 1e-3]
    np.testing.assert_array_equal(error, [0, 1])


def test_damped_least_squares_bounds_gain_by_accepting_task_residual() -> None:
    damping = 0.1
    values = np.r_[0.0, damping, np.logspace(-8, 4, 100)]
    gains = values / (values**2 + damping**2)
    assert np.max(gains) == pytest.approx(1 / (2 * damping))
    jacobian = np.diag([1.0, 1e-3])
    command = np.linalg.solve(jacobian.T @ jacobian + damping**2 * np.eye(2), [1.0, 1e-3])
    assert command[1] < 0.1
    assert np.linalg.norm(jacobian @ command - [1, 1]) > 0.99


def test_coordinate_units_require_transforming_the_joint_velocity_metric() -> None:
    jacobian = np.array([[2.0, 1.0], [0.0, 1.0]])
    coordinate_map = np.diag([1000.0, 1.0])
    transformed_jacobian = jacobian @ coordinate_map
    transformed_metric = coordinate_map.T @ coordinate_map
    normalization = np.diag(1 / np.sqrt(np.diag(transformed_metric)))
    np.testing.assert_allclose(transformed_jacobian @ normalization, jacobian)
    assert np.linalg.cond(transformed_jacobian) > 100 * np.linalg.cond(jacobian)


def test_force_and_velocity_duality_uses_the_transpose_and_declared_budget() -> None:
    jacobian, metric = np.diag([3.0, 1.0]), np.diag([2.0, 5.0])
    velocity, force = np.array([0.2, -0.4]), np.array([1.0, 2.0])
    torque = jacobian.T @ force
    assert torque @ velocity == pytest.approx(force @ (jacobian @ velocity))
    force_shape = jacobian @ np.linalg.solve(metric, jacobian.T)
    assert force @ force_shape @ force == pytest.approx(torque @ np.linalg.solve(metric, torque))


def test_truss_assembly_requires_node_incidence_and_has_translation_null_modes() -> None:
    direction = np.array([0.6, 0.8, 0.0])
    extension_row = np.r_[-direction, direction]
    stiffness = 100 * np.outer(extension_row, extension_row)
    assert stiffness.shape == (6, 6)
    assert np.linalg.matrix_rank(stiffness) == 1
    translation = np.tile([0.3, -0.2, 0.7], 2)
    np.testing.assert_allclose(stiffness @ translation, 0, atol=1e-14)


def test_generic_cross_dyad_is_not_a_conservative_spring() -> None:
    stiffness = np.array([[0.0, 0.0], [1.0, 0.0]])
    assert not np.allclose(stiffness, stiffness.T)
    corners = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]])
    work = sum(
        (stiffness @ ((start + end) / 2)) @ (end - start)
        for start, end in zip(corners[:-1], corners[1:], strict=True)
    )
    assert work == 1


def test_mass_congruence_and_force_duality_preserve_energy_and_power() -> None:
    basis = np.array([[2.0, 1.0], [0.0, 1.0]])
    mass = np.diag([2.0, 3.0])
    rate, torque = np.array([0.2, 0.7]), np.array([3.0, -1.0])
    new_mass = basis.T @ mass @ basis
    assert rate @ new_mass @ rate == pytest.approx((basis @ rate) @ mass @ (basis @ rate))
    assert (basis.T @ torque) @ rate == pytest.approx(torque @ (basis @ rate))
    assert not np.allclose(np.linalg.eigvalsh(new_mass), np.linalg.eigvalsh(mass))


@pytest.mark.parametrize("path", [PRINT, WEB], ids=["print", "web"])
@pytest.mark.parametrize(
    "phrase",
    ["Instantaneous Rank and Finite-Time Control", "What the Pseudoinverse Does Not Guarantee"],
)
def test_both_editions_explain_the_key_scope_distinctions(path: Path, phrase: str) -> None:
    assert phrase in path.read_text(encoding="utf-8")


def test_instantaneously_hidden_velocity_is_observable_over_time() -> None:
    dynamics = np.array([[0.0, 1.0], [0.0, 0.0]])
    measurement = np.array([[1.0, 0.0]])
    hidden = np.array([0.0, 1.0])
    assert np.linalg.norm(measurement @ hidden) == 0
    observation = np.vstack([measurement, measurement @ dynamics])
    np.testing.assert_allclose(observation, np.eye(2))


def test_absolute_angle_double_pendulum_frequencies_follow_energy_matrices() -> None:
    length = 0.5
    mass = length**2 * np.array([[2.0, 1.0], [1.0, 1.0]])
    stiffness = GRAVITY_M_S2 * length * np.diag([2.0, 1.0])
    frequencies_squared = np.linalg.eigvals(np.linalg.solve(mass, stiffness))
    expected = GRAVITY_M_S2 / length * np.array([2 - np.sqrt(2), 2 + np.sqrt(2)])
    np.testing.assert_allclose(np.sort(frequencies_squared), expected)
