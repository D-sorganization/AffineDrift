"""Contracts for the source-only mocap/C3D publication package."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from scripts.verify_mocap_c3d_publication import (
    PUBLICATION_SCHEMA_ID,
    MocapC3DPublicationError,
    verify_publication_package,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "markerless_mocap" / "c3d_publication"
SEVEN_PATH = FIXTURE_DIR / "synthetic_7_camera_v1.json"
EIGHT_PATH = FIXTURE_DIR / "synthetic_8_camera_v1.json"
SCHEMA_PATH = REPO_ROOT / "schemas" / "mocap_c3d_publication_compatibility_v1.schema.json"
SIDECAR_SCHEMA_PATH = REPO_ROOT / "schemas" / "mocap_c3d_loss_sidecar_v1.schema.json"
ARTICLE_PATH = REPO_ROOT / "articles" / "markerless-mocap-c3d-interchange.qmd"


@pytest.fixture
def seven_camera() -> dict[str, Any]:
    """Return an isolated seven-camera publication fixture."""

    return json.loads(SEVEN_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def eight_camera() -> dict[str, Any]:
    """Return an isolated eight-camera publication fixture."""

    return json.loads(EIGHT_PATH.read_text(encoding="utf-8"))


def test_repository_fixtures_are_deterministic_and_dependency_bounded() -> None:
    seven = verify_publication_package(SEVEN_PATH)
    eight = verify_publication_package(EIGHT_PATH)

    assert seven == verify_publication_package(SEVEN_PATH)
    assert seven.camera_count == 7
    assert seven.representable_mask == 127
    assert seven.overflow_count == 0
    assert eight.camera_count == 8
    assert eight.representable_mask is None
    assert eight.overflow_count == 1
    assert eight.loss_count > seven.loss_count
    assert seven.tools_m1_protected_revision is None
    assert eight.tools_m9_protected_revision is None


Mutation = Callable[[dict[str, Any]], None]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["dependencies"]["tools_m1"].update(
                state="available", protected_revision="0" * 40
            ),
            "must remain unavailable with null pins",
        ),
        (
            lambda data: data["timebase"].update(point_rate_hz=199.5),
            "integer multiple",
        ),
        (
            lambda data: data["frames"][0].update(timestamp_ns=1),
            "fixed-rate timestamp",
        ),
        (
            lambda data: data["frames"][0]["points"][0].update(residual=-1.0),
            "negative residual",
        ),
        (
            lambda data: data["events"].extend(copy.deepcopy(data["events"]) * 18),
            "18-event header limit",
        ),
        (
            lambda data: data["c3d_projection"]["points"][0].update(contributor_mask=255),
            "seven-bit contributor mask",
        ),
    ],
)
def test_fixture_rejects_false_authority_or_invalid_c3d_semantics(
    seven_camera: dict[str, Any], mutation: Mutation, message: str
) -> None:
    mutation(seven_camera)

    with pytest.raises(MocapC3DPublicationError, match=message):
        verify_publication_package(seven_camera, fixture_dir=FIXTURE_DIR)


def test_eight_camera_fixture_cannot_silently_select_a_subset(
    eight_camera: dict[str, Any],
) -> None:
    eight_camera["c3d_projection"]["points"][0]["contributor_mask"] = 127

    with pytest.raises(MocapC3DPublicationError, match="must be unavailable"):
        verify_publication_package(eight_camera, fixture_dir=FIXTURE_DIR)


def test_loss_sidecar_digest_and_overflow_are_binding(
    eight_camera: dict[str, Any], tmp_path: Path
) -> None:
    sidecar_name = eight_camera["loss_sidecar"]["path"]
    payload = (FIXTURE_DIR / sidecar_name).read_bytes()
    (tmp_path / sidecar_name).write_bytes(payload.replace(b"camera-08", b"camera-99", 1))

    with pytest.raises(MocapC3DPublicationError, match="SHA-256"):
        verify_publication_package(eight_camera, fixture_dir=tmp_path)


def test_publication_schema_and_reader_guidance_are_versioned() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    sidecar_schema = json.loads(SIDECAR_SCHEMA_PATH.read_text(encoding="utf-8"))
    article = ARTICLE_PATH.read_text(encoding="utf-8")
    spec = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "AGENT_HANDOFF.md").read_text(encoding="utf-8")

    assert schema["properties"]["schema"]["const"] == PUBLICATION_SCHEMA_ID
    assert sidecar_schema["properties"]["schema"]["const"].endswith("loss-sidecar/v1")
    assert "Seven-camera contributor-mask limit" in article
    assert "normalized semantic agreement" in article
    assert "Mocap C3D Publication Compatibility" in spec
    assert "AffineDrift #3959" in handoff
