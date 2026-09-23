"""Independent mechanics and intervention checks for the counterfactual chapter."""

from itertools import product
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

GRAVITY_M_S2 = 9.81
ROOT = Path(__file__).resolve().parents[1]


def _mass(angles: np.ndarray) -> np.ndarray:
    """Assemble the illustrative uniform-rod inertia from Cartesian COM Jacobians."""
    first, second = angles[0], angles.sum()
    tangent_first = np.array([-np.sin(first), np.cos(first)])
    tangent_second = np.array([-np.sin(second), np.cos(second)])
    proximal = np.column_stack((0.2 * tangent_first, np.zeros(2)))
    distal = np.column_stack((0.4 * tangent_first + 0.15 * tangent_second, 0.15 * tangent_second))
    return (
        2 * proximal.T @ proximal
        + 0.2 * distal.T @ distal
        + np.diag([2 * 0.4**2 / 12, 0])
        + 0.2 * 0.3**2 / 12 * np.ones((2, 2))
    )


def _potential(angles: np.ndarray) -> float:
    """Use the two COM heights in the declared upward-positive inertial frame."""
    return float(GRAVITY_M_S2 * (0.48 * np.sin(angles[0]) + 0.03 * np.sin(angles.sum())))


def _bias(angles: np.ndarray, rates: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate the claimed closed-form velocity and gravity bias for comparison."""
    coupling = 0.012 * np.sin(angles[1])
    velocity = coupling * np.array([-(2 * rates[0] * rates[1] + rates[1] ** 2), rates[0] ** 2])
    gravity = GRAVITY_M_S2 * np.array(
        [0.48 * np.cos(angles[0]) + 0.03 * np.cos(angles.sum()), 0.03 * np.cos(angles.sum())]
    )
    return velocity, gravity


def test_mass_matches_cartesian_kinetic_energy_at_multiple_postures() -> None:
    """Catch missing parallel-axis terms and mixed pivot/COM conventions."""
    for distal in [-2.1, 0.0, np.deg2rad(70), np.pi]:
        cosine = np.cos(distal)
        claimed = np.array(
            [
                [2 * 0.4**2 / 3 + 0.032 + 0.006 + 0.024 * cosine, 0.006 + 0.012 * cosine],
                [0.006 + 0.012 * cosine, 0.006],
            ]
        )
        assert claimed == pytest.approx(_mass(np.array([0.4, distal])))
        assert np.all(np.linalg.eigvalsh(claimed) > 0)


def test_velocity_bias_matches_finite_difference_euler_lagrange() -> None:
    """Derive Christoffel forces independently from the Cartesian mass matrix."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    step = 1e-5
    derivative = np.array(
        [
            (_mass(angles + axis * step) - _mass(angles - axis * step)) / (2 * step)
            for axis in np.eye(2)
        ]
    )
    mass_rate = np.einsum("k,kij->ij", rates, derivative)
    energy_gradient = 0.5 * np.einsum("i,kij,j->k", rates, derivative, rates)
    expected = mass_rate @ rates - energy_gradient
    velocity, _ = _bias(angles, rates)
    assert velocity == pytest.approx(expected, rel=1e-9)
    assert rates @ velocity == pytest.approx(0.5 * rates @ mass_rate @ rates)


def test_gravity_matches_potential_gradient_with_correct_angle_sum() -> None:
    """Check every gravity term without relying on the printed force arithmetic."""
    angles, step = np.deg2rad([45, 70]), 1e-5
    numerical = np.array(
        [
            (_potential(angles + axis * step) - _potential(angles - axis * step)) / (2 * step)
            for axis in np.eye(2)
        ]
    )
    _, gravity = _bias(angles, np.zeros(2))
    assert gravity == pytest.approx(numerical, rel=1e-9)
    assert np.cos(angles.sum()) == pytest.approx(-0.4226182617)


def test_snapshot_and_inverse_input_use_the_complete_coupled_matrix() -> None:
    """Check the acceleration ledger and reject diagonal-only input recovery."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    mass = _mass(angles)
    velocity, gravity = _bias(angles, rates)
    zero_input = np.linalg.solve(mass, -velocity - gravity)
    assert zero_input == pytest.approx([11.69948358, -119.25363140])
    reference = np.array([2.0, 8.0])
    recovered = mass @ (reference - zero_input)
    assert recovered == pytest.approx([-0.19700856, 0.66551586], abs=1e-8)
    assert np.linalg.solve(mass, recovered - velocity - gravity) == pytest.approx(reference)
    assert not np.allclose(recovered, np.diag(mass) * (reference - zero_input))


def test_zero_velocity_slice_and_uniform_rate_scaling() -> None:
    """Gravity remains fixed while rigid velocity bias scales quadratically."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    mass = _mass(angles)
    velocity, gravity = _bias(angles, rates)
    doubled, unchanged = _bias(angles, 2 * rates)
    assert doubled == pytest.approx(4 * velocity)
    assert unchanged == pytest.approx(gravity)
    zero_velocity = np.linalg.solve(mass, -gravity)
    assert zero_velocity == pytest.approx([-25.13413141, 63.05631560])
    assert not np.allclose(-doubled - gravity, 4 * (-velocity - gravity))


def test_projected_box_control_bound_matches_all_vertices() -> None:
    """DCR must use the acceleration operator and every declared input bound."""
    angles, rates = np.deg2rad([45, 70]), np.array([8.0, 12.0])
    mass = _mass(angles)
    row = np.linalg.solve(mass, np.eye(2))[1]
    bounds = np.array([2.0, 0.2])
    analytic = np.abs(row) @ bounds
    vertices = [abs(row @ (bounds * signs)) for signs in product([-1, 1], repeat=2)]
    assert analytic == pytest.approx(max(vertices))
    assert analytic == pytest.approx(62.29919587)
    velocity, gravity = _bias(angles, rates)
    ratio = abs(np.linalg.solve(mass, -velocity - gravity)[1]) / analytic
    assert ratio == pytest.approx(1.914208197)


def test_equal_norm_ratios_can_have_different_cancellation_authority() -> None:
    """A scalar magnitude ratio loses the orientation of the input range."""
    drift = np.array([1.0, 0.0])
    parallel, transverse = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    assert np.linalg.norm(parallel) == np.linalg.norm(transverse)
    assert drift - parallel == pytest.approx([0, 0])
    assert np.linalg.norm(drift - transverse) > 0
    assert np.linalg.matrix_rank(np.column_stack((transverse, drift))) == 2


def test_zero_velocity_reset_can_violate_a_moving_constraint() -> None:
    """The support q=t requires velocity one; setting velocity zero is infeasible."""
    constraint_velocity = np.array([[1.0]])
    assert constraint_velocity @ np.array([1.0]) == pytest.approx([1])
    assert not np.allclose(constraint_velocity @ np.zeros(1), [1])


def test_pointwise_subtraction_remains_exact_after_branch_separation() -> None:
    """The identity needs a common state, not a particular time index."""
    solution = solve_ivp(lambda _time, state: state**2 + 1, (0, 0.5), [0], rtol=1e-10)
    state = solution.y[0, -1]
    assert (state**2 + 1) - state**2 == pytest.approx(1)
    assert (state**2 + 1) - 0**2 != pytest.approx(1)
    assert state == pytest.approx(np.tan(0.5), rel=1e-7)


def test_large_acceleration_does_not_imply_stiffness() -> None:
    """Constant acceleration has no rapidly decaying eigenmode and integrates exactly."""
    acceleration, duration = 1e6, 0.01
    solution = solve_ivp(lambda _time, state: [state[1], acceleration], (0, duration), [0, 0])
    assert solution.y[:, -1] == pytest.approx(
        [0.5 * acceleration * duration**2, acceleration * duration]
    )
    assert np.linalg.eigvals([[0, 1], [0, 0]]) == pytest.approx([0, 0])


def test_published_editions_replace_the_incorrect_mechanics() -> None:
    """Require corrected worked values in both editions and reject known wrong claims."""
    book = ROOT / "articles/The_Physics_of_Golf"
    for relative in [
        "chapters/ch06_zero_torque_counterfactual.tex",
        "quarto/ch06_zero_torque_counterfactual.qmd",
    ]:
        source = (book / relative).read_text(encoding="utf-8")
        for value in ["0.152875", "-3.788841", "11.699484", "-119.253631", "-0.197009", "0.665516"]:
            assert value in source, f"{relative}: missing verified worked value {value}"
        assert "C_2 = 0" not in source
        assert "via force plates or instrumented clubs" not in source
    standalone = (ROOT / "articles/zero-torque-counterfactual.qmd").read_text(encoding="utf-8")
    assert "exact only at $t=t_0$" not in standalone
    assert "invisible in raw inverse dynamics" not in standalone
    assert "drift acceleration vector at $x_k$" not in standalone
