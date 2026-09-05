"""Independent numerical checks for the inverse-dynamics chapter revision."""

from pathlib import Path

import numpy as np
import pytest

BOOK = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"


def test_measurement_must_remove_the_actual_load_null_space() -> None:
    matrix = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, -1.0]])
    invisible = np.array([-1.0, 1.0, 1.0])
    np.testing.assert_allclose(matrix @ invisible, 0.0)
    assert np.linalg.matrix_rank(np.vstack((matrix, [1.0, 1.0, 0.0]))) == 2
    independent = np.vstack((matrix, [0.0, 0.0, 1.0]))
    assert np.linalg.matrix_rank(independent) == 3
    np.testing.assert_allclose(
        np.linalg.solve(independent, [2 / 3, 1 / 3, -1 / 3]), [1.0, 0.0, -1 / 3]
    )
    assert np.linalg.det(matrix[:, [0, 2]]) == -1.0  # One actuator can be identifiable.


def test_weighted_inference_changes_without_changing_force_balance() -> None:
    matrix = np.array([[1.0, 1.0]])
    inverse_weight = np.diag([1.0, 1 / 4])
    inferred = (
        inverse_weight @ matrix.T @ np.linalg.solve(matrix @ inverse_weight @ matrix.T, [10.0])
    )
    np.testing.assert_allclose(inferred, [8.0, 2.0])
    np.testing.assert_allclose(matrix @ inferred, [10.0])
    assert inferred @ np.diag([1.0, 4.0]) @ inferred == pytest.approx(80.0)


def test_wrench_transport_preserves_power_and_changes_moment() -> None:
    offset = np.array([0.2, 0.0, 0.0])
    force = np.array([0.0, 100.0, 0.0])
    moment_at_hand = np.array([0.0, 0.0, 3.0])
    omega = np.array([0.0, 0.0, 2.0])
    velocity_origin = np.array([1.0, 0.0, 0.0])
    velocity_hand = velocity_origin + np.cross(omega, offset)
    moment_origin = moment_at_hand + np.cross(offset, force)
    np.testing.assert_allclose(moment_origin, [0.0, 0.0, 23.0])
    assert moment_origin @ omega + force @ velocity_origin == pytest.approx(46.0)
    assert moment_at_hand @ omega + force @ velocity_hand == pytest.approx(46.0)


def test_vertical_force_offset_does_not_create_yaw_moment() -> None:
    moment = np.cross([0.2, -0.1, 0.0], [0.0, 0.0, 1400.0])
    np.testing.assert_allclose(moment, [-140.0, -280.0, 0.0])
    assert 1400 / (100 * 9.81) == pytest.approx(1.4271151886)


def test_small_inertia_reduces_absolute_inverse_acceleration_error() -> None:
    for epsilon in [0.1, 0.01]:
        mass = np.diag([1.0, epsilon])
        torque_error = mass @ np.array([0.1, 0.1])
        acceleration_error = np.linalg.solve(mass, [0.1, 0.1])
        np.testing.assert_allclose(torque_error, [0.1, 0.1 * epsilon])
        np.testing.assert_allclose(acceleration_error, [0.1, 0.1 / epsilon])
        assert np.linalg.cond(mass) == pytest.approx(1 / epsilon)
    assert np.linalg.cond(1000 * np.eye(2)) == 1.0


def test_straight_two_link_arm_has_regular_physical_inertia() -> None:
    mass = np.array([[8 / 3, 5 / 6], [5 / 6, 1 / 3]])
    task = np.array([[0.0, 0.0], [2.0, 1.0]])
    assert np.linalg.matrix_rank(task) == 1
    assert np.linalg.det(mass) == pytest.approx(7 / 36)
    assert np.linalg.eigvalsh(mass).min() > 0.0


def test_wheatstone_bridge_uses_declared_voltage_dividers() -> None:
    resistance = 350.0
    strain = 500e-6
    factor = 2.0
    delta = factor * strain
    output_ratio = resistance / (resistance * (1 + delta) + resistance) - 0.5
    assert output_ratio == pytest.approx(-delta / (4 + 2 * delta))
    assert 5 * output_ratio == pytest.approx(-0.00124937531234)
    assert output_ratio == pytest.approx(-factor * strain / 4, rel=0.001)


def test_piezoelectric_charge_is_converted_by_capacitance() -> None:
    charge = 4e-12 * 100.0
    assert charge == pytest.approx(400e-12)
    assert charge / 200e-12 == pytest.approx(2.0)
    assert -charge / 1e-9 == pytest.approx(-0.4)


def test_forward_branch_difference_is_not_same_state_input() -> None:
    # q'' = -q + u, initially q=q'=0, constant u=1.
    time = np.pi / 2
    position_actual = 1 - np.cos(time)
    acceleration_actual = np.cos(time)
    position_zero = acceleration_zero = 0.0
    same_state_zero = -position_actual
    assert acceleration_actual - acceleration_zero == pytest.approx(0.0, abs=1e-14)
    assert acceleration_actual - same_state_zero == pytest.approx(1.0)
    assert position_actual - position_zero == pytest.approx(1.0)


@pytest.mark.parametrize(
    "edition",
    ["chapters/ch18_inverse_dynamics_parallel.tex", "quarto/ch18_inverse_dynamics_parallel.qmd"],
)
def test_chapter_does_not_reintroduce_invalid_inference(edition: str) -> None:
    text = (BOOK / edition).read_text(encoding="utf-8")
    for phrase in [
        "the ground actively powers the downswing",
        "load distribution must favor the right arm",
        "Direct measurement of muscle activation",
        "same club position and orientation",
        "Why Forward Works but Inverse Doesn",
        "Vaughan's Resolution Strategy",
    ]:
        assert phrase not in text
