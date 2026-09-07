"""Independent physical checks for the screw-axis textbook examples."""

import importlib
from typing import Any

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.spatial.transform import Rotation


@pytest.fixture(scope="module")
def example() -> Any:
    """Import the implementation only after collecting the physical contracts."""
    return importlib.import_module("src.tools.screw_examples")


@pytest.mark.parametrize("angle", [0.0, 0.4, -1.8, np.pi])
def test_frame_change_matches_point_velocity_and_force_moment(example: Any, angle: float) -> None:
    """Compare the six-vector transform with direct three-vector mechanics."""
    rotation = Rotation.from_rotvec(np.array([0.0, 0.0, angle])).as_matrix()
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = [0.7, -0.4, 0.2]
    point_b = np.array([0.3, 0.2, -0.1])
    force_b = np.array([4.0, -2.0, 3.0])
    couple_b = np.array([0.5, 0.1, -0.2])
    twist_b = np.array([0.8, -0.3, 0.4, 1.0, 0.6, -0.2])
    wrench_b = np.r_[np.cross(point_b, force_b) + couple_b, force_b]
    twist_a = example.adjoint(transform) @ twist_b
    wrench_a = example.reexpress_wrench(transform, wrench_b)
    point_a = rotation @ point_b + transform[:3, 3]
    speed_b = twist_b[3:] + np.cross(twist_b[:3], point_b)
    speed_a = twist_a[3:] + np.cross(twist_a[:3], point_a)
    np.testing.assert_allclose(speed_a, rotation @ speed_b, atol=1e-14)
    np.testing.assert_allclose(
        wrench_a[:3], np.cross(point_a, rotation @ force_b) + rotation @ couple_b, atol=1e-14
    )
    np.testing.assert_allclose(wrench_a[3:], rotation @ force_b, atol=1e-14)
    direct_power = force_b @ speed_b + couple_b @ twist_b[:3]
    assert wrench_a @ twist_a == pytest.approx(direct_power)


@pytest.mark.parametrize("angle", [1e-5, 0.4, 2.4, np.pi - 1e-9, np.pi])
def test_finite_axis_reproduces_displacement_of_every_point(example: Any, angle: float) -> None:
    """Construct a displacement from a geometric axis, then recover its line."""
    direction = np.array([1.0, -2.0, 3.0]) / np.sqrt(14)
    point = np.array([0.7, 0.2, -0.1])
    point -= (point @ direction) * direction
    rotation = Rotation.from_rotvec(angle * direction).as_matrix()
    axial = 0.2 * angle
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = point - rotation @ point + axial * direction
    screw = example.finite_screw(transform)
    np.testing.assert_allclose(screw.point, point, atol=2e-11)
    assert screw.angle == pytest.approx(angle)
    for material_point in (np.zeros(3), np.array([1.0, 2.0, 3.0]), point):
        recovered = rotation @ (material_point - screw.point) + screw.point
        recovered += screw.axial_displacement * screw.direction
        np.testing.assert_allclose(
            recovered, rotation @ material_point + transform[:3, 3], atol=2e-11
        )
    np.testing.assert_allclose(screw.point @ screw.direction, 0, atol=1e-14)
    assert screw.pitch * screw.angle == pytest.approx(screw.axial_displacement)


@pytest.mark.parametrize("translation", [[0, 0, 0], [1, -2, 3]])
def test_translation_has_no_unique_rotational_axis(example: Any, translation: list[int]) -> None:
    """Reject the undefined finite-axis branch instead of dividing by zero."""
    transform = np.eye(4)
    transform[:3, 3] = translation
    with pytest.raises(ValueError, match="rotation"):
        example.finite_screw(transform)


def test_absolute_pose_is_not_the_interpose_displacement(example: Any) -> None:
    """An offset initial body frame cancels from T1 inverse(T0)."""
    initial = np.eye(4)
    initial[:3, 3] = [2, 3, 4]
    displacement = np.eye(4)
    displacement[:3, :3] = Rotation.from_euler("z", 0.5).as_matrix()
    final = displacement @ initial
    recovered = example.finite_screw(final @ np.linalg.inv(initial))
    np.testing.assert_allclose(recovered.point, 0, atol=1e-14)
    assert np.linalg.norm(example.finite_screw(final).point) > 1


def test_first_order_twist_step_is_not_an_exact_rigid_transform(example: Any) -> None:
    """Matrix exponentiation preserves rigidity; a finite Euler step does not."""
    generator = np.zeros((4, 4))
    generator[0, 1], generator[1, 0], generator[0, 3] = -0.1, 0.1, 1
    approximate = np.eye(4) + generator * 0.1
    with pytest.raises(ValueError, match="rotation"):
        example.adjoint(approximate)
    screw = example.finite_screw(expm(generator * 0.1))
    np.testing.assert_allclose(screw.point, [0, 10, 0], atol=1e-11)
    assert screw.pitch == pytest.approx(0)


@pytest.mark.parametrize("load_x", [1.0, 2.0, 2.5, 3.0])
def test_four_bar_solves_each_body_balance_and_virtual_power(example: Any, load_x: float) -> None:
    """Check all three moving links and the complete assembly independently."""
    result = example.four_bar_equilibrium(load_x, 100.0)
    a, b, c, d = np.array([[0, 0], [1, 1], [3, 1], [4, 0]], dtype=float)
    force_b, force_c, torque = result.force_b, result.force_c, result.torque_a
    external = np.array([0.0, -100.0])

    def moment(position: np.ndarray, force: np.ndarray) -> float:
        """Evaluate a planar moment without a spatial-vector helper."""
        return float(position[0] * force[1] - position[1] * force[0])

    np.testing.assert_allclose(force_b + force_c + external, 0, atol=1e-13)
    assert moment(b - a, -force_b) + torque == pytest.approx(0, abs=1e-13)
    assert moment(c - d, -force_c) == pytest.approx(0, abs=1e-13)
    assert moment(c - b, force_c) + moment(np.array([load_x, 1]) - b, external) == pytest.approx(
        0, abs=1e-13
    )
    assert moment(d - a, force_c) + torque - 100 * load_x == pytest.approx(0, abs=1e-13)
    # Unit input angular speed gives v_B=(-1,1), omega_BC=-1, v_E,y=2-x_E.
    assert torque - 100 * (2 - load_x) == pytest.approx(0, abs=1e-13)
    if load_x == 2:
        assert torque == pytest.approx(0)
        np.testing.assert_allclose(force_b, [50, 50])
        np.testing.assert_allclose(force_c, [-50, 50])


@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((3, 3)),
        np.full((4, 4), np.nan),
        np.diag([-1.0, 1.0, 1.0, 1.0]),
        np.diag([1, 1, 1, 2]),
    ],
)
def test_transform_contract_rejects_nonrigid_inputs(example: Any, bad: np.ndarray) -> None:
    """Reject wrong size, nonfinite, reflecting and nonhomogeneous inputs."""
    with pytest.raises(ValueError):
        example.adjoint(bad)


def test_bad_wrench_and_load_contracts(example: Any) -> None:
    """Reject malformed loads and invalid parameters at the public boundary."""
    for wrench in (np.zeros(3), np.full(6, np.inf)):
        with pytest.raises(ValueError):
            example.reexpress_wrench(np.eye(4), wrench)
    for position, load in ((float("nan"), 1), (2, -1), (2, float("inf"))):
        with pytest.raises(ValueError):
            example.four_bar_equilibrium(position, load)
