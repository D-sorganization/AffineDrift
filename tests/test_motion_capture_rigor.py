"""Independent manufactured examples for motion-capture interpretation."""

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ARTICLE = Path(__file__).resolve().parents[1] / "articles/technology-motion-capture.qmd"


@pytest.mark.parametrize("baseline, expected_mm", [(1.0, 5.0), (0.2, 25.0)])
def test_stereo_depth_sensitivity(baseline: float, expected_mm: float) -> None:
    focal_pixels, depth, disparity_sigma = 1000.0, 5.0, 0.2
    disparity = focal_pixels * baseline / depth
    step = 1e-4
    slope = (
        focal_pixels * baseline / (disparity + step) - focal_pixels * baseline / (disparity - step)
    ) / (2 * step)
    assert abs(slope) * disparity_sigma * 1000 == pytest.approx(expected_mm, rel=1e-7)


def test_sampling_exposure_and_sync_are_distinct() -> None:
    speed = 45.0
    np.testing.assert_allclose(
        speed / np.array([200, 300, 360, 500, 1000]), [0.225, 0.15, 0.125, 0.09, 0.045]
    )
    assert speed * 50e-6 == pytest.approx(0.00225)
    assert speed * 0.001 == pytest.approx(0.045)
    assert 1 / (2 * 300) * 1000 == pytest.approx(1.6666666667)


def test_aliasing_survives_short_exposure() -> None:
    sample_times = np.arange(30) / 300
    np.testing.assert_allclose(
        np.sin(2 * np.pi * 220 * sample_times),
        np.sin(2 * np.pi * -80 * sample_times),
        atol=5e-14,
    )


def test_acceleration_noise_from_independent_positions() -> None:
    weights = np.array([1, -2, 1]) / 0.01**2
    variance = weights @ (1e-6 * np.eye(3)) @ weights
    assert np.sqrt(variance) == pytest.approx(24.4948974278)


@pytest.mark.parametrize("correlation, expected", [(0, 8), (0.75, 2), (-0.75, 14)])
def test_relative_scalar_variance(correlation: float, expected: float) -> None:
    covariance = 4 * np.array([[1, correlation], [correlation, 1]])
    difference = np.array([1, -1])
    assert difference @ covariance @ difference == pytest.approx(expected)


def test_common_rotation_cancels_exactly() -> None:
    pelvis = Rotation.from_rotvec([0.4, -0.2, 0.1]).as_matrix()
    thorax = Rotation.from_rotvec([-0.2, 0.7, 0.4]).as_matrix()
    error = Rotation.from_rotvec([0.5, 0.3, -0.4]).as_matrix()
    np.testing.assert_allclose((error @ pelvis).T @ (error @ thorax), pelvis.T @ thorax)


def test_two_endpoints_do_not_observe_roll() -> None:
    landmarks = np.array([[0, 0, 0], [0, 0, 1], [1, 0, 0]])
    turned = Rotation.from_euler("z", 73, degrees=True).apply(landmarks)
    np.testing.assert_allclose(turned[:2], landmarks[:2])
    assert np.linalg.norm(turned[2] - landmarks[2]) > 1


def test_axis_point_and_pitch_reconstruct_velocity_field() -> None:
    omega, origin_velocity = np.array([0.0, 0, 2]), np.array([1.0, 0, 0.2])
    axis_point = np.cross(omega, origin_velocity) / (omega @ omega)
    pitch = omega @ origin_velocity / (omega @ omega)
    np.testing.assert_allclose(axis_point, [0, 0.5, 0])
    assert pitch == pytest.approx(0.1)
    for height in [-2.0, 0, 3.0]:
        point = axis_point + height * omega
        np.testing.assert_allclose(origin_velocity + np.cross(omega, point), pitch * omega)


def test_pitch_is_not_invariant_to_a_different_observer() -> None:
    omega, velocity = np.array([0, 0, 2.0]), np.array([1.0, 0, 0.2])
    assert omega @ velocity / (omega @ omega) == pytest.approx(0.1)
    assert omega @ (velocity - [0, 0, 0.2]) == pytest.approx(0)


def test_constant_pitch_does_not_determine_energy() -> None:
    inertia = np.diag([1.0, 2.0, 3.0])
    omega = np.array([0.0, 0, 2.0])
    assert 0.5 * omega @ inertia @ omega == pytest.approx(6)
    assert 0.5 * (2 * omega) @ inertia @ (2 * omega) == pytest.approx(24)
    # Pure rotation about the stationary centre has zero pitch at both speeds.
    assert omega @ np.zeros(3) == 0


def test_axis_direction_conditioning_depends_on_signal_size() -> None:
    angles = []
    for rate in [1.0, 0.01]:
        observed = np.array([0.01, 0.0, rate])
        angles.append(np.degrees(np.arctan2(observed[0], observed[2])))
    np.testing.assert_allclose(angles, [0.5729386977, 45.0])


def test_different_velocity_scalars_reverse_peak_order() -> None:
    times = np.linspace(0, 0.3, 3001)
    x = np.exp(-(((times - 0.1) / 0.025) ** 2))
    y = 2 * np.exp(-(((times - 0.2) / 0.025) ** 2))
    other = np.exp(-(((times - 0.15) / 0.025) ** 2))
    assert times[x.argmax()] < times[other.argmax()]
    assert times[np.hypot(x, y).argmax()] > times[other.argmax()]


def test_reference_point_error_changes_moment() -> None:
    np.testing.assert_allclose(np.cross([0.01, 0, 0], [0, 0, 1000]), [0, -10, 0])


@pytest.mark.parametrize(
    "unsupported",
    [
        "Instrumentation error is sub-millimetre and essentially solved.",
        "This is the physical origin of club-marker blur",
        "a three-sensor system reproduced trunk and pelvic rotation",
    ],
)
def test_withdrawn_technical_claims_do_not_return(unsupported: str) -> None:
    assert unsupported not in ARTICLE.read_text(encoding="utf-8")
