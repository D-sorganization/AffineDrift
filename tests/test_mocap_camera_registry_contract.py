"""Contracts for the markerless-mocap camera evidence registry."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from scripts.verify_mocap_camera_registry import (
    REGISTRY_SCHEMA_ID,
    CameraRegistryError,
    verify_camera_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "data" / "markerless_mocap" / "camera_evidence_registry_v1.json"
SCHEMA_PATH = REPO_ROOT / "schemas" / "mocap_camera_evidence_registry_v1.schema.json"
ARTICLE_PATH = REPO_ROOT / "articles" / "markerless-mocap-camera-selection.qmd"


@pytest.fixture
def registry() -> dict[str, Any]:
    """Return an isolated copy of the governed registry."""

    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_repository_registry_is_deterministic_and_fail_closed(registry: dict[str, Any]) -> None:
    first = verify_camera_registry(registry)
    second = verify_camera_registry(copy.deepcopy(registry))

    assert first == second
    assert first.camera_count == 3
    assert first.source_count >= 10
    assert first.claim_count >= 30
    assert first.recommendation_count == 2
    assert first.unavailable_claim_count >= 3
    assert first.procurement_approved_count == 0


Mutation = Callable[[dict[str, Any]], None]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["claims"][0].update(source_ids=[]),
            "requires at least one source",
        ),
        (
            lambda data: data["claims"][0].update(evidence_class="engineering_inference"),
            "engineering inference must remain provisional",
        ),
        (
            lambda data: next(
                claim for claim in data["claims"] if claim["status"] == "unavailable"
            ).update(value="unknown"),
            "unavailable claim must use null",
        ),
        (
            lambda data: data["claims"][1].update(id=data["claims"][0]["id"]),
            "duplicate claim id",
        ),
        (
            lambda data: data["cameras"][0]["purchasing_claim_ids"].append("missing-claim"),
            "unknown claim id",
        ),
        (
            lambda data: data["recommendations"][0].update(status="approved"),
            "may not approve procurement",
        ),
        (
            lambda data: data["cameras"][0]["purchasing_claim_ids"].pop(),
            "purchasing attributes differ",
        ),
        (
            lambda data: data["sources"][0].update(url="http://example.com/spec"),
            "HTTPS",
        ),
    ],
)
def test_registry_rejects_unqualified_or_untraceable_purchasing_claims(
    registry: dict[str, Any], mutation: Mutation, message: str
) -> None:
    mutation(registry)

    with pytest.raises(CameraRegistryError, match=message):
        verify_camera_registry(registry)


def test_registry_rejects_camera_claim_owned_by_another_model(registry: dict[str, Any]) -> None:
    first_camera = registry["cameras"][0]
    second_camera = registry["cameras"][1]
    first_camera["purchasing_claim_ids"][0] = second_camera["purchasing_claim_ids"][0]

    with pytest.raises(CameraRegistryError, match="belongs to"):
        verify_camera_registry(registry)


def test_registry_schema_and_reader_guidance_are_versioned() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    article = ARTICLE_PATH.read_text(encoding="utf-8")
    spec = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "AGENT_HANDOFF.md").read_text(encoding="utf-8")

    assert schema["properties"]["schema"]["const"] == REGISTRY_SCHEMA_ID
    assert "Provisional Shop Recommendation" in article
    assert "buy two cameras for the pilot" in article
    assert "Camera Evidence Registry" in spec
    assert "AffineDrift #3956" in handoff
