#!/usr/bin/env python3
"""Contract verification for the synthetic camera-geometry teaching fixture."""

from __future__ import annotations

import math
import re

from scripts.mocap_camera_geometry_math import project_point
from scripts.mocap_camera_geometry_probes import verify_probes
from scripts.mocap_camera_geometry_types import (
    CameraGeometryFixtureError,
    CameraGeometrySummary,
)
from scripts.mocap_camera_geometry_validation import (
    matrix3,
    nonempty_array,
    nonempty_text,
    numeric_vector,
    object_with_keys,
)

GEOMETRY_SCHEMA_ID = "affinedrift/mocap-camera-geometry-fixture/v1"
DEPENDENCY_IDS = frozenset({"tools_m4_intrinsics", "tools_m5_extrinsics"})
REVISION = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
PIXEL_TOLERANCE = 1e-9

_array = nonempty_array
_matrix3 = matrix3
_object = object_with_keys
_text = nonempty_text
_vector = numeric_vector


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
        observation = _object(
            item, f"observation {index}", {"camera_id", "point_id", "expected_pixel"}
        )
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


def verify_camera_geometry_fixture(value: object) -> CameraGeometrySummary:
    """Validate one synthetic teaching fixture without claiming solver authority."""

    fixture = _object(
        value,
        "fixture",
        {
            "schema",
            "fixture_id",
            "classification",
            "authority",
            "dependencies",
            "coordinate_convention",
            "cameras",
            "world_points",
            "observations",
            "probes",
        },
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
    pixel, depth, sigma = verify_probes(fixture["probes"])
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
