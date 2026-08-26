"""Contracts for the markerless-mocap camera-geometry teaching fixture."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.verify_mocap_camera_geometry_fixture import (
    GEOMETRY_SCHEMA_ID,
    CameraGeometryFixtureError,
    verify_camera_geometry_fixture,
    verify_fixture_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "data" / "markerless_mocap" / "camera_geometry_fixture_v1.json"
SCHEMA_PATH = REPO_ROOT / "schemas" / "mocap_camera_geometry_fixture_v1.schema.json"
ARTICLE_PATH = REPO_ROOT / "articles" / "markerless-mocap-camera-geometry.qmd"


@pytest.fixture
def fixture() -> dict[str, Any]:
    """Return an isolated copy of the governed synthetic fixture."""

    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_repository_fixture_is_pinned_and_deterministic(fixture: dict[str, Any]) -> None:
    first = verify_camera_geometry_fixture(fixture)
    second = verify_camera_geometry_fixture(copy.deepcopy(fixture))

    assert first == second
    assert verify_fixture_file(FIXTURE_PATH) == first
    assert first.camera_count == 2
    assert first.point_count == 3
    assert first.observation_count == 6
    assert first.dependency_count == 2
    assert first.available_dependency_count == 0
    assert first.calibration_authority_available is False
    assert first.maximum_projection_error_px <= 1e-9


def test_projection_equations_include_brown_conrady_distortion(
    fixture: dict[str, Any],
) -> None:
    summary = verify_camera_geometry_fixture(fixture)

    assert summary.distortion_probe_pixel == pytest.approx((951.096, 126.578), abs=1e-9)
    assert summary.stereo_depth_m == pytest.approx(5.0, abs=1e-12)
    assert summary.stereo_depth_sigma_m == pytest.approx(0.02209708691207961, rel=1e-12)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["authority"].update(runtime_authority=True),
            "must not claim calibration runtime authority",
        ),
        (
            lambda data: data["dependencies"].pop(),
            "dependencies must be exactly",
        ),
        (
            lambda data: data["dependencies"][0].update(status="available"),
            "available dependency requires immutable",
        ),
        (
            lambda data: data["observations"][0]["expected_pixel"].__setitem__(0, 0.0),
            "projection mismatch",
        ),
        (
            lambda data: data["probes"]["synchronization"].update(action="accept"),
            "unsynchronized observations must be rejected",
        ),
        (
            lambda data: data["probes"]["movement"].update(expected_state="valid"),
            "movement state mismatch",
        ),
        (
            lambda data: data["probes"]["observability"].pop("bundle_adjustment_gauge"),
            "observability probes must be exactly",
        ),
    ],
)
def test_fixture_fails_closed_on_authority_or_geometry_violation(
    fixture: dict[str, Any], mutation: Any, message: str
) -> None:
    mutation(fixture)

    with pytest.raises(CameraGeometryFixtureError, match=message):
        verify_camera_geometry_fixture(fixture)


def test_schema_manual_spec_and_handoff_expose_dependency_boundary() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    article = ARTICLE_PATH.read_text(encoding="utf-8")
    spec = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "AGENT_HANDOFF.md").read_text(encoding="utf-8")
    quarto = (REPO_ROOT / "_quarto.yml").read_text(encoding="utf-8")

    assert schema["$id"].endswith("mocap_camera_geometry_fixture_v1.schema.json")
    assert schema["properties"]["schema"]["const"] == GEOMETRY_SCHEMA_ID
    for term in (
        "Intrinsics and Distortion",
        "Direct Linear Transform",
        "Perspective-n-Point",
        "Bundle Adjustment",
        "Observability and Gauge Freedom",
        "Uncertainty Propagation",
        "Movement Rejection and Recalibration",
        "Unsynchronized Observations",
    ):
        assert term in article
    assert "Tools #4714" in article
    assert "Tools #4721" in article
    assert "status: `unavailable`" in article
    assert "Camera Geometry Pedagogy Contract" in spec
    assert "AffineDrift #3962" in handoff
    assert "markerless-mocap-camera-geometry.html" in quarto
