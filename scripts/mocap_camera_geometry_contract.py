#!/usr/bin/env python3
"""Contract verification for the synthetic camera-geometry teaching fixture."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import cast

from scripts.mocap_camera_geometry_math import (
    distort_brown_conrady,
    euclidean_distance,
    pixel_from_normalized,
    project_point,
    rectified_stereo_depth_uncertainty,
)

GEOMETRY_SCHEMA_ID = "affinedrift/mocap-camera-geometry-fixture/v1"
DEPENDENCY_IDS = frozenset({"tools_m4_intrinsics", "tools_m5_extrinsics"})
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
REVISION = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
PIXEL_TOLERANCE = 1e-9


class CameraGeometryFixtureError(RuntimeError):
    """Raised when camera-geometry pedagogy violates its fail-closed contract."""


@dataclass(frozen=True)
class CameraGeometrySummary:
    """Deterministic evidence from one accepted synthetic fixture."""

    camera_count: int
    point_count: int
    observation_count: int
    dependency_count: int
    available_dependency_count: int
    calibration_authority_available: bool
    maximum_projection_error_px: float
    distortion_probe_pixel: tuple[float, float]
    stereo_depth_m: float
    stereo_depth_sigma_m: float


def _object(value: object, label: str, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraGeometryFixtureError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise CameraGeometryFixtureError(
            f"{label} fields differ: missing={sorted(keys - actual)}, "
            f"extra={sorted(actual - keys)}"
        )
    return result


def _array(value: object, label: str, length: int | None = None) -> list[object]:
    if not isinstance(value, list) or not value:
        raise CameraGeometryFixtureError(f"{label} must be a non-empty array")
    result = cast(list[object], value)
    if length is not None and len(result) != length:
        raise CameraGeometryFixtureError(f"{label} must contain {length} values")
    return result


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CameraGeometryFixtureError(f"{label} must be a non-empty string")
    return value


def _number(value: object, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise CameraGeometryFixtureError(f"{label} must be finite")
    result = float(value)
    if positive and result <= 0.0:
        raise CameraGeometryFixtureError(f"{label} must be positive")
    return result


def _vector(value: object, label: str, length: int) -> tuple[float, ...]:
    return tuple(_number(item, f"{label} item") for item in _array(value, label, length))


def _matrix3(value: object, label: str) -> tuple[tuple[float, ...], ...]:
    rows = _array(value, label, 3)
    return tuple(_vector(row, f"{label} row", 3) for row in rows)


def _verify_authority(value: object) -> None:
    authority = _object(
        value,
        "authority",
        {"repository", "purpose", "runtime_authority", "procurement_authority"},
    )
    if _text(authority["repository"], "authority repository") != "D-sorganization/AffineDrift":
        raise CameraGeometryFixtureError("AffineDrift must remain the pedagogy authority")
    if _text(authority["purpose"], "authority purpose") != "synthetic_pedagogy_only":
        raise CameraGeometryFixtureError("authority purpose must remain synthetic pedagogy only")
    if authority["runtime_authority"] is not False:
        raise CameraGeometryFixtureError("fixture must not claim calibration runtime authority")
    if authority["procurement_authority"] is not False:
        raise CameraGeometryFixtureError("fixture must not claim procurement authority")


def _verify_dependency(value: object, index: int) -> tuple[str, bool]:
    dependency = _object(
        value,
        f"dependency {index}",
        {
            "id",
            "authority_repository",
            "issue_url",
            "status",
            "protected_revision",
            "schema_id",
            "fixture_sha256",
            "limitation",
        },
    )
    dependency_id = _text(dependency["id"], f"dependency {index} id")
    if _text(dependency["authority_repository"], "dependency authority") != "D-sorganization/Tools":
        raise CameraGeometryFixtureError("camera-geometry runtime authority must remain Tools")
    _text(dependency["limitation"], f"dependency {dependency_id} limitation")
    status = _text(dependency["status"], f"dependency {dependency_id} status")
    pins = (
        dependency["protected_revision"],
        dependency["schema_id"],
        dependency["fixture_sha256"],
    )
    if status == "unavailable":
        if any(pin is not None for pin in pins):
            raise CameraGeometryFixtureError("unavailable dependency must not carry authority pins")
        return dependency_id, False
    if status != "available":
        raise CameraGeometryFixtureError(f"dependency {dependency_id} status is unsupported")
    revision, schema_id, digest = pins
    if not isinstance(revision, str) or REVISION.fullmatch(revision) is None:
        raise CameraGeometryFixtureError("available dependency requires immutable revision pin")
    if not isinstance(schema_id, str) or not schema_id.strip():
        raise CameraGeometryFixtureError("available dependency requires immutable schema id")
    if not isinstance(digest, str) or DIGEST.fullmatch(digest) is None:
        raise CameraGeometryFixtureError("available dependency requires immutable fixture digest")
    return dependency_id, True


def _verify_dependencies(value: object) -> tuple[int, int]:
    identifiers: set[str] = set()
    available = 0
    for index, item in enumerate(_array(value, "dependencies")):
        dependency_id, is_available = _verify_dependency(item, index)
        if dependency_id in identifiers:
            raise CameraGeometryFixtureError(f"duplicate dependency id: {dependency_id}")
        identifiers.add(dependency_id)
        available += int(is_available)
    if identifiers != DEPENDENCY_IDS:
        raise CameraGeometryFixtureError("dependencies must be exactly Tools M4 and Tools M5")
    return len(identifiers), available


def _verify_convention(value: object) -> None:
    convention = _object(value, "coordinate convention", {"world", "camera", "image", "units"})
    expected = {
        "world": "right_handed_x_right_y_down_z_forward",
        "camera": "world_to_camera_Xc_equals_R_Xw_plus_t",
        "image": "u_right_v_down_pixel_centres",
        "units": "metres_radians_pixels_seconds",
    }
    if convention != expected:
        raise CameraGeometryFixtureError("coordinate convention differs from the fixture contract")


def _verify_camera(value: object, index: int) -> tuple[str, dict[str, object]]:
    camera = _object(value, f"camera {index}", {"id", "K", "distortion", "R", "t"})
    camera_id = _text(camera["id"], f"camera {index} id")
    _matrix3(camera["K"], f"camera {camera_id} K")
    _vector(camera["distortion"], f"camera {camera_id} distortion", 5)
    _matrix3(camera["R"], f"camera {camera_id} R")
    _vector(camera["t"], f"camera {camera_id} t", 3)
    return camera_id, camera


def _verify_cameras(value: object) -> dict[str, dict[str, object]]:
    cameras: dict[str, dict[str, object]] = {}
    for index, item in enumerate(_array(value, "cameras")):
        camera_id, camera = _verify_camera(item, index)
        if camera_id in cameras:
            raise CameraGeometryFixtureError(f"duplicate camera id: {camera_id}")
        cameras[camera_id] = camera
    return cameras


def _verify_points(value: object) -> dict[str, tuple[float, ...]]:
    points: dict[str, tuple[float, ...]] = {}
    for index, item in enumerate(_array(value, "world points")):
        point = _object(item, f"world point {index}", {"id", "xyz_m"})
        point_id = _text(point["id"], f"world point {index} id")
        if point_id in points:
            raise CameraGeometryFixtureError(f"duplicate world point id: {point_id}")
        points[point_id] = _vector(point["xyz_m"], f"world point {point_id}", 3)
    return points


def _project(camera: dict[str, object], point: tuple[float, ...]) -> tuple[float, float]:
    try:
        return project_point(
            _matrix3(camera["K"], "camera K"),
            _vector(camera["distortion"], "distortion", 5),
            _matrix3(camera["R"], "camera R"),
            _vector(camera["t"], "camera t", 3),
            point,
        )
    except ValueError as error:
        raise CameraGeometryFixtureError(str(error)) from error


def _verify_observations(
    value: object,
    cameras: dict[str, dict[str, object]],
    points: dict[str, tuple[float, ...]],
) -> tuple[int, float]:
    maximum_error = 0.0
    pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(_array(value, "observations")):
        observation = _object(item, f"observation {index}", {"camera_id", "point_id", "expected_pixel"})
        camera_id = _text(observation["camera_id"], "observation camera id")
        point_id = _text(observation["point_id"], "observation point id")
        if camera_id not in cameras or point_id not in points:
            raise CameraGeometryFixtureError("observation references an unknown camera or point")
        pair = (camera_id, point_id)
        if pair in pairs:
            raise CameraGeometryFixtureError(f"duplicate observation: {pair}")
        pairs.add(pair)
        expected = _vector(observation["expected_pixel"], "expected pixel", 2)
        actual = _project(cameras[camera_id], points[point_id])
        error = math.hypot(actual[0] - expected[0], actual[1] - expected[1])
        maximum_error = max(maximum_error, error)
    if maximum_error > PIXEL_TOLERANCE:
        raise CameraGeometryFixtureError(f"projection mismatch: {maximum_error:.12g} px")
    return len(pairs), maximum_error


def _verify_distortion_probe(value: object) -> tuple[float, float]:
    probe = _object(value, "distortion probe", {"normalized_point", "K", "coefficients", "expected_pixel"})
    normalized_raw = _vector(probe["normalized_point"], "distortion normalized point", 2)
    normalized = (normalized_raw[0], normalized_raw[1])
    distorted = distort_brown_conrady(
        normalized, _vector(probe["coefficients"], "distortion coefficients", 5)
    )
    pixel = pixel_from_normalized(distorted, _matrix3(probe["K"], "distortion K"))
    expected = _vector(probe["expected_pixel"], "distortion expected pixel", 2)
    if math.hypot(pixel[0] - expected[0], pixel[1] - expected[1]) > PIXEL_TOLERANCE:
        raise CameraGeometryFixtureError("distortion probe mismatch")
    return pixel


def _verify_stereo_probe(value: object) -> tuple[float, float]:
    probe = _object(
        value,
        "stereo uncertainty probe",
        {"focal_length_px", "baseline_m", "disparity_px", "pixel_sigma_px", "expected_depth_m", "expected_depth_sigma_m"},
    )
    focal = _number(probe["focal_length_px"], "stereo focal length", positive=True)
    baseline = _number(probe["baseline_m"], "stereo baseline", positive=True)
    disparity = _number(probe["disparity_px"], "stereo disparity", positive=True)
    pixel_sigma = _number(probe["pixel_sigma_px"], "pixel sigma", positive=True)
    depth, sigma = rectified_stereo_depth_uncertainty(focal, baseline, disparity, pixel_sigma)
    expected_depth = _number(probe["expected_depth_m"], "expected depth", positive=True)
    expected_sigma = _number(probe["expected_depth_sigma_m"], "expected depth sigma", positive=True)
    if not math.isclose(depth, expected_depth, abs_tol=1e-12):
        raise CameraGeometryFixtureError("stereo depth mismatch")
    if not math.isclose(sigma, expected_sigma, rel_tol=1e-12):
        raise CameraGeometryFixtureError("stereo uncertainty mismatch")
    return depth, sigma


def _verify_synchronization_probe(value: object) -> None:
    probe = _object(value, "synchronization probe", {"speed_m_s", "time_skew_s", "maximum_skew_s", "expected_spatial_m", "action"})
    speed = _number(probe["speed_m_s"], "synchronization speed", positive=True)
    skew = _number(probe["time_skew_s"], "time skew", positive=True)
    maximum = _number(probe["maximum_skew_s"], "maximum skew", positive=True)
    expected = _number(probe["expected_spatial_m"], "expected spatial offset", positive=True)
    if not math.isclose(speed * skew, expected, abs_tol=1e-12):
        raise CameraGeometryFixtureError("synchronization spatial-offset mismatch")
    if skew > maximum and probe["action"] != "reject":
        raise CameraGeometryFixtureError("unsynchronized observations must be rejected")


def _verify_movement_probe(value: object) -> None:
    probe = _object(
        value,
        "movement probe",
        {"baseline_center_m", "observed_center_m", "translation_limit_m", "rotation_delta_deg", "rotation_limit_deg", "expected_state", "action"},
    )
    baseline = _vector(probe["baseline_center_m"], "baseline centre", 3)
    observed = _vector(probe["observed_center_m"], "observed centre", 3)
    translation = euclidean_distance(baseline, observed)
    moved = translation > _number(probe["translation_limit_m"], "translation limit", positive=True)
    moved |= _number(probe["rotation_delta_deg"], "rotation delta") > _number(
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
        probe = _object(item, f"observability probe {probe_id}", {"status", "reason"})
        if _text(probe["status"], f"observability probe {probe_id} status") not in {
            "ambiguous",
            "model_conditioned",
            "rejected",
            "unavailable",
        }:
            raise CameraGeometryFixtureError(f"observability probe {probe_id} status is unsupported")
        _text(probe["reason"], f"observability probe {probe_id} reason")


def _verify_probes(value: object) -> tuple[tuple[float, float], float, float]:
    probes = _object(
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


def verify_camera_geometry_fixture(value: object) -> CameraGeometrySummary:
    """Validate one synthetic teaching fixture without claiming solver authority."""

    fixture = _object(
        value,
        "fixture",
        {"schema", "fixture_id", "classification", "authority", "dependencies", "coordinate_convention", "cameras", "world_points", "observations", "probes"},
    )
    if _text(fixture["schema"], "schema") != GEOMETRY_SCHEMA_ID:
        raise CameraGeometryFixtureError(f"schema must be {GEOMETRY_SCHEMA_ID}")
    _text(fixture["fixture_id"], "fixture id")
    if _text(fixture["classification"], "classification") != "model_scenario":
        raise CameraGeometryFixtureError("synthetic fixture must remain a model scenario")
    _verify_authority(fixture["authority"])
    dependency_count, available = _verify_dependencies(fixture["dependencies"])
    _verify_convention(fixture["coordinate_convention"])
    cameras = _verify_cameras(fixture["cameras"])
    points = _verify_points(fixture["world_points"])
    observation_count, maximum_error = _verify_observations(
        fixture["observations"], cameras, points
    )
    pixel, depth, sigma = _verify_probes(fixture["probes"])
    return CameraGeometrySummary(
        len(cameras),
        len(points),
        observation_count,
        dependency_count,
        available,
        available == dependency_count,
        maximum_error,
        pixel,
        depth,
        sigma,
    )
