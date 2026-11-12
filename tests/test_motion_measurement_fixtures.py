"""Known-answer checks for the MM-2 motion-measurement fixtures (#5410).

Every input is synthetic and seeded. Tolerances are stated next to each assertion.
"""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from src.tools import motion_measurement_fixtures as mm

EXACT = 1e-12


def test_cardan_sequences_give_different_angles_for_one_orientation() -> None:
    matrix = Rotation.from_euler("XYZ", [0.4, 0.7, -0.5]).as_matrix()
    xyz = mm.cardan_angles(matrix, "XYZ")
    zyx = mm.cardan_angles(matrix, "ZYX")
    np.testing.assert_allclose(xyz, [0.4, 0.7, -0.5], atol=EXACT)
    assert np.max(np.abs(xyz - zyx[::-1])) > 0.1
    np.testing.assert_allclose(Rotation.from_euler("ZYX", zyx).as_matrix(), matrix, atol=EXACT)


def test_cardan_rejects_unknown_sequence() -> None:
    with pytest.raises(ValueError, match="Cardan"):
        mm.cardan_angles(np.eye(3), "ZXZ")


@pytest.mark.parametrize("pitch", [np.pi / 2, -np.pi / 2])
def test_gimbal_lock_detected_at_ninety_degrees_only(pitch: float) -> None:
    locked = Rotation.from_euler("ZYX", [0.3, pitch, 0.2]).as_matrix()
    free = Rotation.from_euler("ZYX", [0.3, pitch * 0.9, 0.2]).as_matrix()
    assert mm.is_gimbal_locked(locked, "ZYX")
    assert not mm.is_gimbal_locked(free, "ZYX")


def test_unwrap_removes_the_180_degree_jump() -> None:
    truth = np.linspace(0.0, 2.0 * np.pi, 50)
    wrapped = np.arctan2(np.sin(truth), np.cos(truth))
    assert np.max(np.abs(np.diff(wrapped))) > np.pi
    np.testing.assert_allclose(mm.unwrap_angles(wrapped), truth, atol=EXACT)


def test_svd_reorthogonalisation_returns_nearest_proper_rotation() -> None:
    rng = np.random.default_rng(mm.SEED)
    truth = Rotation.from_rotvec([0.3, -0.5, 0.8]).as_matrix()
    drifted = truth + 1e-3 * rng.standard_normal((3, 3))
    fixed = mm.nearest_rotation(drifted)
    np.testing.assert_allclose(fixed @ fixed.T, np.eye(3), atol=EXACT)
    assert np.linalg.det(fixed) == pytest.approx(1.0, abs=EXACT)
    assert np.linalg.norm(fixed - truth) < np.linalg.norm(drifted - truth)


def test_svd_reorthogonalisation_rejects_nonfinite_input() -> None:
    with pytest.raises(ValueError, match="finite"):
        mm.nearest_rotation(np.full((3, 3), np.nan))


def test_hemisphere_continuity_removes_sign_flips_without_changing_orientation() -> None:
    angles = np.linspace(0.0, 1.5 * np.pi, 40)
    smooth = Rotation.from_rotvec(np.outer(angles, [0.0, 0.0, 1.0])).as_quat()
    flips = np.where(np.arange(40) % 3 == 0, -1.0, 1.0)[:, None]
    fixed = mm.hemisphere_continuous(smooth * flips)
    assert np.min(np.sum(fixed[1:] * fixed[:-1], axis=1)) > 0.0
    np.testing.assert_allclose(np.abs(np.sum(fixed * smooth, axis=1)), 1.0, atol=EXACT)


def test_helical_axis_error_shrinks_as_the_step_grows() -> None:
    errors = [mm.helical_axis_error(step, 1e-3, 500) for step in (0.02, 0.1, 0.5)]
    assert errors[0] > errors[1] > errors[2]
    assert errors[0] / errors[2] > 10.0  # roughly inverse to the rotation size


def test_finite_axis_bias_grows_with_step_on_a_precessing_axis() -> None:
    steps = (0.01, 0.1, 0.3, 1.0)
    bias = [mm.moving_axis_error(step, 1e-3, 200)["bias_rad"] for step in steps]
    assert bias == sorted(bias)
    assert bias[0] < 1e-4 and bias[-1] > 0.05  # rad: finite axis drifts from the instantaneous one


def test_noisy_finite_axis_error_is_u_shaped_with_an_interior_minimum() -> None:
    steps = (0.01, 0.1, 0.3, 1.0)
    noisy = [mm.moving_axis_error(step, 1e-3, 500)["noisy_error_rad"] for step in steps]
    assert int(np.argmin(noisy)) in (1, 2)  # neither the smallest nor the largest step
    assert noisy[0] > 5.0 * min(noisy) and noisy[-1] > 5.0 * min(noisy)


def test_moving_axis_rejects_a_nonpositive_step() -> None:
    with pytest.raises(ValueError, match="positive"):
        mm.moving_axis_error(0.0, 1e-3, 10)


def test_poisson_omega_is_exact_and_euler_difference_is_not() -> None:
    result = mm.euler_vs_poisson(dt=1e-3)
    assert result["poisson_max_error"] < 1e-5  # rad/s, central scheme on a smooth path
    assert result["euler_difference_max_error"] > 0.1  # rad/s, wrong quantity


def test_euler_difference_error_grows_toward_gimbal_lock() -> None:
    near = mm.euler_vs_poisson(dt=1e-3, pitch=np.deg2rad(85.0))
    far = mm.euler_vs_poisson(dt=1e-3, pitch=np.deg2rad(30.0))
    assert near["euler_difference_mean_error"] > far["euler_difference_mean_error"]


def test_quaternion_filtering_needs_sign_continuity() -> None:
    without = mm.filtered_quaternion_min_norm(window=5, continuity=False)
    with_fix = mm.filtered_quaternion_min_norm(window=5, continuity=True)
    assert without < 0.5
    assert with_fix > 0.99


def test_noise_error_is_independent_of_omega_and_truncation_scales_as_omega_cubed() -> None:
    slow = mm.difference_errors(omega=1.0, sigma=1e-3, dt=1e-2)
    fast = mm.difference_errors(omega=2.0, sigma=1e-3, dt=1e-2)
    assert fast["noise_rms"] / slow["noise_rms"] == pytest.approx(1.0, rel=0.1)
    assert fast["truncation_max"] / slow["truncation_max"] == pytest.approx(8.0, rel=0.05)


def test_results_are_deterministic_and_round_trip_through_json(tmp_path: Path) -> None:
    first = mm.write_results(tmp_path / "a.json")
    second = mm.write_results(tmp_path / "b.json")
    assert first == second
    assert json.loads((tmp_path / "a.json").read_text(encoding="utf-8")) == first
    assert {
        "gimbal",
        "helical_axis",
        "moving_axis",
        "angular_velocity",
        "quaternion",
        "differences",
    } <= set(first)
