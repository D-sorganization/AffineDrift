"""Independent probe checks for the camera-geometry teaching fixture."""

from __future__ import annotations

import math
from typing import cast

from scripts.mocap_camera_geometry_math import (
    distort_brown_conrady,
    euclidean_distance,
    pixel_from_normalized,
    rectified_stereo_depth_uncertainty,
)
from scripts.mocap_camera_geometry_types import CameraGeometryFixtureError
from scripts.mocap_camera_geometry_validation import (
    finite_number,
    matrix3,
    nonempty_text,
    numeric_vector,
    object_with_keys,
)

OBSERVABILITY_IDS = frozenset(
    {
        "bundle_adjustment_gauge",
        "dlt_coplanar",
        "intrinsic_planar_target",
        "pnp_planar",
        "single_view_depth",
        "unsynchronized_multiview",
    }
)
PIXEL_TOLERANCE = 1e-9


def _verify_distortion_probe(value: object) -> tuple[float, float]:
    probe = object_with_keys(
        value, "distortion probe", {"normalized_point", "K", "coefficients", "expected_pixel"}
    )
    normalized_raw = numeric_vector(probe["normalized_point"], "distortion normalized point", 2)
    normalized = (normalized_raw[0], normalized_raw[1])
    distorted = distort_brown_conrady(
        normalized, numeric_vector(probe["coefficients"], "distortion coefficients", 5)
    )
    pixel = pixel_from_normalized(distorted, matrix3(probe["K"], "distortion K"))
    expected = numeric_vector(probe["expected_pixel"], "distortion expected pixel", 2)
    if math.hypot(pixel[0] - expected[0], pixel[1] - expected[1]) > PIXEL_TOLERANCE:
        raise CameraGeometryFixtureError("distortion probe mismatch")
    return pixel


def _verify_stereo_probe(value: object) -> tuple[float, float]:
    probe = object_with_keys(
        value,
        "stereo uncertainty probe",
        {
            "focal_length_px",
            "baseline_m",
            "disparity_px",
            "pixel_sigma_px",
            "expected_depth_m",
            "expected_depth_sigma_m",
        },
    )
    focal = finite_number(probe["focal_length_px"], "stereo focal length", positive=True)
    baseline = finite_number(probe["baseline_m"], "stereo baseline", positive=True)
    disparity = finite_number(probe["disparity_px"], "stereo disparity", positive=True)
    pixel_sigma = finite_number(probe["pixel_sigma_px"], "pixel sigma", positive=True)
    depth, sigma = rectified_stereo_depth_uncertainty(focal, baseline, disparity, pixel_sigma)
    expected_depth = finite_number(probe["expected_depth_m"], "expected depth", positive=True)
    expected_sigma = finite_number(
        probe["expected_depth_sigma_m"], "expected depth sigma", positive=True
    )
    if not math.isclose(depth, expected_depth, abs_tol=1e-12):
        raise CameraGeometryFixtureError("stereo depth mismatch")
    if not math.isclose(sigma, expected_sigma, rel_tol=1e-12):
        raise CameraGeometryFixtureError("stereo uncertainty mismatch")
    return depth, sigma


def _verify_synchronization_probe(value: object) -> None:
    probe = object_with_keys(
        value,
        "synchronization probe",
        {"speed_m_s", "time_skew_s", "maximum_skew_s", "expected_spatial_m", "action"},
    )
    speed = finite_number(probe["speed_m_s"], "synchronization speed", positive=True)
    skew = finite_number(probe["time_skew_s"], "time skew", positive=True)
    maximum = finite_number(probe["maximum_skew_s"], "maximum skew", positive=True)
    expected = finite_number(probe["expected_spatial_m"], "expected spatial offset", positive=True)
    if not math.isclose(speed * skew, expected, abs_tol=1e-12):
        raise CameraGeometryFixtureError("synchronization spatial-offset mismatch")
    if skew > maximum and probe["action"] != "reject":
        raise CameraGeometryFixtureError("unsynchronized observations must be rejected")


def _verify_movement_probe(value: object) -> None:
    probe = object_with_keys(
        value,
        "movement probe",
        {
            "baseline_center_m",
            "observed_center_m",
            "translation_limit_m",
            "rotation_delta_deg",
            "rotation_limit_deg",
            "expected_state",
            "action",
        },
    )
    baseline = numeric_vector(probe["baseline_center_m"], "baseline centre", 3)
    observed = numeric_vector(probe["observed_center_m"], "observed centre", 3)
    translation = euclidean_distance(baseline, observed)
    moved = translation > finite_number(
        probe["translation_limit_m"], "translation limit", positive=True
    )
    moved |= finite_number(probe["rotation_delta_deg"], "rotation delta") > finite_number(
        probe["rotation_limit_deg"], "rotation limit", positive=True
    )
    state = "invalidated" if moved else "valid"
    if probe["expected_state"] != state:
        raise CameraGeometryFixtureError("movement state mismatch")
    if moved and probe["action"] != "reject_and_recalibrate":
        raise CameraGeometryFixtureError("camera movement must require rejection and recalibration")


def _verify_observability(value: object) -> None:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraGeometryFixtureError("observability probes must be an object")
    probes = cast(dict[str, object], value)
    if set(probes) != OBSERVABILITY_IDS:
        raise CameraGeometryFixtureError("observability probes must be exactly the governed cases")
    for probe_id, item in probes.items():
        probe = object_with_keys(item, f"observability probe {probe_id}", {"status", "reason"})
        if nonempty_text(probe["status"], f"observability probe {probe_id} status") not in {
            "ambiguous",
            "model_conditioned",
            "rejected",
            "unavailable",
        }:
            raise CameraGeometryFixtureError(
                f"observability probe {probe_id} status is unsupported"
            )
        nonempty_text(probe["reason"], f"observability probe {probe_id} reason")


def verify_probes(value: object) -> tuple[tuple[float, float], float, float]:
    """Verify every independent equation and failure-state probe."""

    probes = object_with_keys(
        value,
        "probes",
        {"distortion", "stereo_uncertainty", "synchronization", "movement", "observability"},
    )
    pixel = _verify_distortion_probe(probes["distortion"])
    depth, sigma = _verify_stereo_probe(probes["stereo_uncertainty"])
    _verify_synchronization_probe(probes["synchronization"])
    _verify_movement_probe(probes["movement"])
    _verify_observability(probes["observability"])
    return pixel, depth, sigma
