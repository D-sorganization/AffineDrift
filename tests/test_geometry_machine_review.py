"""Independent geometric counterexamples and Chapter 4 publication checks."""

import importlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/illustrations/preload_transmission_study.npz"


def test_figure_shows_distance_perpendicular_to_force_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    module = importlib.import_module("make_proximal_distal_companion_expanded_figures")
    captured = []
    monkeypatch.setattr(module, "_save", lambda figure, stem: captured.append(figure))
    module.make_moment_arm()
    try:
        for axis in captured[0].axes:
            lines = {line.get_gid(): line for line in axis.lines}
            assert "force-line-of-action" in lines
            assert "perpendicular-moment-arm" in lines
            force = lines["force-line-of-action"].get_xydata()
            arm = lines["perpendicular-moment-arm"].get_xydata()
            direction = force[-1] - force[0]
            distance = arm[-1] - arm[0]
            assert direction @ distance == pytest.approx(0, abs=1e-12)
            offset = arm[-1] - force[0]
            assert np.linalg.det(np.stack([offset, direction])) == pytest.approx(0, abs=1e-12)
            np.testing.assert_allclose(arm[0], [0, 0])
    finally:
        plt.close("all")


def test_reference_transport_preserves_rigid_body_wrench_power() -> None:
    force, moment = np.array([3.0, -2, 5]), np.array([1.0, 4, -3])
    velocity, omega = np.array([2.0, 1, -1]), np.array([0.5, -1, 2])
    shift = np.array([0.4, -0.3, 0.2])
    shifted_moment = moment - np.cross(shift, force)
    shifted_velocity = velocity + np.cross(omega, shift)
    power = force @ velocity + moment @ omega
    assert force @ shifted_velocity + shifted_moment @ omega == pytest.approx(power)
    assert force @ velocity + shifted_moment @ omega != pytest.approx(power)


def test_change_of_observer_is_not_just_a_change_of_components() -> None:
    force = np.array([3.0, -2, 5])
    velocity, observer_velocity = np.array([2.0, 1, -1]), np.array([1.0, 0, 0])
    assert force @ (velocity - observer_velocity) - force @ velocity == -3.0


def test_prescribed_base_motion_contributes_power_outside_joint_coordinates() -> None:
    jacobian = np.array([[1.0, 2], [-1, 0]])
    rates, base_velocity, force = np.array([2.0, 3]), np.array([4.0, -2]), np.array([3.0, 5])
    hand_velocity = jacobian @ rates + base_velocity
    generalized = jacobian.T @ force
    assert force @ hand_velocity == generalized @ rates + force @ base_velocity
    assert force @ hand_velocity != generalized @ rates


def test_near_singular_velocity_and_force_requirements_scale_oppositely() -> None:
    for epsilon in (0.1, 0.01):
        jacobian = np.diag([1.0, epsilon])
        rates = np.linalg.solve(jacobian, [0.0, 1.0])
        generalized = jacobian.T @ np.array([0.0, 10.0])
        assert rates[1] == 1 / epsilon
        assert generalized[1] == pytest.approx(10 * epsilon)
    singular = np.diag([1.0, 0])
    np.testing.assert_allclose(singular.T @ np.array([0.0, 10]), [0, 0])
    np.testing.assert_allclose(singular.T @ np.array([0.0, 100]), [0, 0])


def test_positive_off_diagonal_inertia_can_give_negative_cross_acceleration() -> None:
    mass = np.array([[2.0, 1], [1, 2]])
    acceleration = np.linalg.solve(mass, [1.0, 0])
    np.testing.assert_allclose(acceleration, [2 / 3, -1 / 3])
    rotation = np.array([[1.0, 1], [1, -1]]) / np.sqrt(2)
    transformed_mass = rotation.T @ mass @ rotation
    np.testing.assert_allclose(transformed_mass, np.diag([3, 1]), atol=1e-15)
    reconstructed = rotation @ np.linalg.solve(transformed_mass, rotation.T @ [1.0, 0])
    np.testing.assert_allclose(reconstructed, acceleration)


def test_couple_reversal_differs_from_corotation() -> None:
    separation, force = np.array([0.04, 0, 0]), np.array([0.0, 100, 0])
    moment = np.cross(separation, force)
    np.testing.assert_allclose(moment, [0, 0, 4])
    np.testing.assert_allclose(np.cross(-separation, force), -moment)
    np.testing.assert_allclose(np.cross(separation, -force), -moment)
    rotation = np.diag([-1.0, -1, 1])
    np.testing.assert_allclose(np.cross(rotation @ separation, rotation @ force), moment)


def test_allocation_archive_matches_only_scalar_control_moment() -> None:
    with np.load(ARCHIVE, allow_pickle=False) as archive:
        net = archive["net_control_moment_nm"]
        direct, contact = archive["direct_wrist_moment_nm"], archive["grip_force_couple_nm"]
        assert net.shape == (19, 21)
        np.testing.assert_allclose(net, 8, atol=6e-15, rtol=0)
        np.testing.assert_allclose(direct + contact, net, atol=5e-15, rtol=0)
        # Even at one configuration the resultant varies across allocations.
        assert np.ptp(archive["hand_force_resultant_n"], axis=1).max() > 1
        assert np.all(direct[:, -1] > net[:, -1])
        assert np.all(contact[:, -1] < 0)


def test_allocation_archive_cost_minima_are_grid_and_metric_specific() -> None:
    with np.load(ARCHIVE, allow_pickle=False) as archive:
        fraction = archive["wrist_fractions"]
        hand = archive["hand_force_rms_n"]
        torque = archive["joint_torque_norm_nm"]
        np.testing.assert_allclose([hand.min(), hand.max()], [7.581686905156809, 91.51213361769024])
        np.testing.assert_allclose(
            [torque.min(), torque.max()], [5.736508698407808, 25.44939024411236]
        )
        hand_minimum, torque_minimum = (
            fraction[hand.argmin(axis=1)],
            fraction[torque.argmin(axis=1)],
        )
        np.testing.assert_allclose([hand_minimum.min(), hand_minimum.max()], [0.75, 0.9])
        np.testing.assert_allclose([torque_minimum.min(), torque_minimum.max()], [0.85, 0.95])
        assert np.all(hand_minimum != torque_minimum)
