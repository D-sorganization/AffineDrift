"""Deterministic synthetic fixtures for the motion-measurement article (MM-2, #5410).

Every input is generated here from a fixed seed; no capture data is used. Rotations act on
column vectors, Cardan sequences are intrinsic (uppercase scipy convention), quaternions are
scalar-last as returned by scipy. Tolerances are stated by the callers (tests), not hidden here.
"""

import json
import warnings
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import uniform_filter1d
from scipy.spatial.transform import Rotation

type Array = NDArray[np.float64]

SEED = 5410
LOCK_TOLERANCE = 1e-6  # rad: |middle angle| within this of pi/2 counts as gimbal lock
CARDAN_SEQUENCES = frozenset({"XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"})
HELICAL_AXIS = np.array([1.0, 2.0, 2.0]) / 3.0


def cardan_angles(matrix: Array, sequence: str) -> Array:
    """Return the three intrinsic Cardan angles of a rotation matrix for one sequence."""
    if sequence not in CARDAN_SEQUENCES:
        raise ValueError(f"Cardan sequence must be a permutation of XYZ, got {sequence!r}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # scipy warns at lock; lock is reported separately
        return np.asarray(Rotation.from_matrix(matrix).as_euler(sequence), dtype=float)


def is_gimbal_locked(matrix: Array, sequence: str) -> bool:
    """True when the middle Cardan angle is within LOCK_TOLERANCE of plus or minus 90 degrees."""
    middle = cardan_angles(matrix, sequence)[1]
    return bool(abs(abs(middle) - np.pi / 2) < LOCK_TOLERANCE)


def unwrap_angles(angles: Array) -> Array:
    """Remove the 2*pi jumps of a wrapped angle series (radians)."""
    return np.unwrap(np.asarray(angles, dtype=float))


def nearest_rotation(matrix: Array) -> Array:
    """Project a drifted 3x3 matrix onto the nearest proper rotation via SVD."""
    value = np.asarray(matrix, dtype=float)
    if value.shape != (3, 3) or not np.isfinite(value).all():
        raise ValueError("matrix must be a finite 3x3 array")
    left, _, right_t = np.linalg.svd(value)
    correction = np.diag([1.0, 1.0, np.sign(np.linalg.det(left @ right_t))])
    return left @ correction @ right_t


def hemisphere_continuous(quats: Array) -> Array:
    """Flip signs so consecutive quaternions have a non-negative dot product."""
    out = np.array(quats, dtype=float)
    dots = np.sum(out[1:] * out[:-1], axis=1)
    out[1:] *= np.cumprod(np.where(dots < 0.0, -1.0, 1.0))[:, None]
    return out


def helical_axis_error(step_angle: float, sigma: float, trials: int) -> float:
    """Mean axis-direction error (rad) of a finite rotation of ``step_angle`` with noise.

    Noise is a random rotation vector of standard deviation ``sigma`` per component, so the
    expected error is roughly ``sigma / step_angle``: small steps give unreliable axes.
    """
    if step_angle <= 0.0 or trials < 1:
        raise ValueError("step_angle must be positive and trials at least 1")
    rng = np.random.default_rng(SEED)
    noise = Rotation.from_rotvec(sigma * rng.standard_normal((trials, 3)))
    estimate = (noise * Rotation.from_rotvec(HELICAL_AXIS * step_angle)).as_rotvec()
    axes = estimate / np.linalg.norm(estimate, axis=1, keepdims=True)
    return float(np.mean(np.arccos(np.clip(axes @ HELICAL_AXIS, -1.0, 1.0))))


def _euler_path(pitch: float, dt: float) -> tuple[Array, Array, Array]:
    """Smooth ZYX path: time, angles (yaw, pitch, roll) and analytic angle rates."""
    time = np.arange(0.0, 1.0 + dt / 2.0, dt)
    angles = np.column_stack([0.3 + 1.2 * time, pitch + 0.05 * np.sin(2 * time), -0.4 + 0.9 * time])
    rates = np.column_stack(
        [np.full_like(time, 1.2), 0.1 * np.cos(2 * time), np.full_like(time, 0.9)]
    )
    return time, angles, rates


def _analytic_spatial_omega(angles: Array, rates: Array) -> Array:
    """Spatial angular velocity of an intrinsic ZYX path: sum of the rate-weighted axes."""
    yaw, pitch = angles[:, 0], angles[:, 1]
    about_z = np.tile([0.0, 0.0, 1.0], (len(angles), 1)) * rates[:, [0]]
    about_y = (
        Rotation.from_rotvec(np.outer(yaw, [0.0, 0.0, 1.0])).apply([0.0, 1.0, 0.0]) * rates[:, [1]]
    )
    about_x = Rotation.from_euler("ZY", np.column_stack([yaw, pitch])).apply([1.0, 0.0, 0.0])
    return np.asarray(about_z + about_y + about_x * rates[:, [2]], dtype=float)


def euler_vs_poisson(dt: float, pitch: float = np.deg2rad(60.0)) -> dict[str, float]:
    """Compare the Poisson (rotation-difference) omega and Euler-rate reading to the truth."""
    _, angles, rates = _euler_path(pitch, dt)
    truth = _analytic_spatial_omega(angles, rates)[1:-1]
    rotations = Rotation.from_euler("ZYX", angles)
    poisson = (rotations[2:] * rotations[:-2].inv()).as_rotvec() / (2.0 * dt)
    naive = np.gradient(angles, dt, axis=0)[1:-1][:, ::-1]  # (roll, pitch, yaw) read as omega
    naive_error = np.linalg.norm(naive - truth, axis=1)
    return {
        "poisson_max_error": float(np.max(np.linalg.norm(poisson - truth, axis=1))),
        "euler_difference_max_error": float(np.max(naive_error)),
        "euler_difference_mean_error": float(np.mean(naive_error)),
    }


def filtered_quaternion_min_norm(window: int, continuity: bool) -> float:
    """Smallest norm after a component-wise moving average of a canonicalised quaternion path.

    The path is a 270 degree turn about z. A library that forces ``w >= 0`` flips the sign once
    the turn passes 180 degrees; averaging across that flip collapses the norm unless the series
    is made hemisphere-continuous first.
    """
    angles = np.linspace(0.0, 1.5 * np.pi, 200)
    quats = Rotation.from_rotvec(np.outer(angles, [0.0, 0.0, 1.0])).as_quat()
    quats = np.where(quats[:, [3]] < 0.0, -quats, quats)
    series = hemisphere_continuous(quats) if continuity else quats
    smoothed = uniform_filter1d(series, size=window, axis=0, mode="nearest")
    return float(np.min(np.linalg.norm(smoothed, axis=1)))


def difference_errors(omega: float, sigma: float, dt: float) -> dict[str, float]:
    """Central-difference rate errors: noise (rms, linear angle) and truncation (sine angle)."""
    time = np.arange(0.0, 20.0, dt)
    noise = sigma * np.random.default_rng(SEED).standard_normal(time.size)
    noisy_rate = np.gradient(omega * time + noise, dt)[1:-1]
    sine_rate = np.gradient(np.sin(omega * time), dt)[1:-1]
    sine_error = sine_rate - omega * np.cos(omega * time[1:-1])
    return {
        "noise_rms": float(np.sqrt(np.mean((noisy_rate - omega) ** 2))),
        "truncation_max": float(np.max(np.abs(sine_error))),
    }


def build_results() -> dict[str, object]:
    """Collect every fixture result that the article figures read."""
    locked = Rotation.from_euler("ZYX", [0.3, np.pi / 2, 0.2]).as_matrix()
    steps = [0.02, 0.1, 0.5]
    return {
        "seed": SEED,
        "gimbal": {"locked_at_90_deg": is_gimbal_locked(locked, "ZYX")},
        "helical_axis": {
            "sigma": 1e-3,
            "steps_rad": steps,
            "mean_axis_error_rad": [helical_axis_error(step, 1e-3, 500) for step in steps],
        },
        "angular_velocity": {
            "pitch_30_deg": euler_vs_poisson(1e-3, np.deg2rad(30.0)),
            "pitch_85_deg": euler_vs_poisson(1e-3, np.deg2rad(85.0)),
        },
        "quaternion": {
            "window": 5,
            "min_norm_without_continuity": filtered_quaternion_min_norm(5, False),
            "min_norm_with_continuity": filtered_quaternion_min_norm(5, True),
        },
        "differences": {
            "omega_1": difference_errors(1.0, 1e-3, 1e-2),
            "omega_2": difference_errors(2.0, 1e-3, 1e-2),
        },
    }


def write_results(path: Path) -> dict[str, object]:
    """Write the results as sorted, indented JSON and return the same dictionary."""
    results = build_results()
    path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results
