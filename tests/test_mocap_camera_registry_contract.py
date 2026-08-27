"""Contracts for the markerless-mocap camera evidence registry."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

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

    return cast(dict[str, Any], json.loads(REGISTRY_PATH.read_text(encoding="utf-8")))


def test_repository_registry_is_deterministic_and_fail_closed(registry: dict[str, Any]) -> None:
    first = verify_camera_registry(registry)
    second = verify_camera_registry(copy.deepcopy(registry))

    assert first == second
    assert first.camera_count == 5
    assert first.source_count >= 16
    assert first.claim_count >= 50
    assert first.recommendation_count == 3
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


def test_zed_synchronization_claim_refreshed_to_15_microseconds(registry: dict[str, Any]) -> None:
    claims_by_id = {claim["id"]: claim for claim in registry["claims"]}
    zed_sync = claims_by_id["zed-sync"]
    article = ARTICLE_PATH.read_text(encoding="utf-8")

    assert "10 microseconds" not in str(zed_sync["value"])
    assert "10 microsecond" not in str(zed_sync["value"])
    assert "15 microseconds" in str(zed_sync["value"])
    assert "within 10 microseconds" not in article
    assert "15 microseconds" in article
    assert any("stereolabs" in s and "sync" in s for s in zed_sync["source_ids"])


def test_price_scoping_contracts_distinguish_camera_body_from_system_cost(
    registry: dict[str, Any],
) -> None:
    claims_by_id = {claim["id"]: claim for claim in registry["claims"]}
    article = ARTICLE_PATH.read_text(encoding="utf-8")

    flir_price = claims_by_id["flir-price"]
    assert flir_price["status"] == "current"
    assert flir_price["evidence_class"] == "vendor_spec"
    assert "371" in str(flir_price["value"])
    assert "camera body only" in flir_price["limitations"].lower()

    zed_price = claims_by_id["zed-price"]
    assert zed_price["status"] == "current"
    assert zed_price["evidence_class"] == "vendor_spec"
    assert "399" in str(zed_price["value"])
    assert "424" in str(zed_price["value"])
    assert "camera body only" in zed_price["limitations"].lower()

    basler_price = claims_by_id["basler-price"]
    assert basler_price["status"] == "unavailable"
    assert basler_price["value"] is None
    assert basler_price["evidence_class"] == "unavailable"

    assert "camera body" in article.lower()
    assert "system cost" in article.lower()


def test_pilot_role_and_distributed_topology_roles_remain_distinct(
    registry: dict[str, Any],
) -> None:
    cameras_by_id = {cam["id"]: cam for cam in registry["cameras"]}
    recommendations_by_id = {rec["id"]: rec for rec in registry["recommendations"]}
    article = ARTICLE_PATH.read_text(encoding="utf-8")

    assert "flir-bfs-u3-16s2c-cs" in cameras_by_id
    assert "basler-a2a1920-160ucbas" in cameras_by_id
    assert "stereolabs-zed-x-one-gs" in cameras_by_id
    assert "allied-alvium-g5-203c" in cameras_by_id
    assert "lucid-triton2-trt016s-cc" in cameras_by_id

    assert "shop-fast-motion-two-camera-pilot" in recommendations_by_id
    assert "shop-distributed-ethernet-reference-evaluation" in recommendations_by_id
    assert "shop-long-cable-evaluation" in recommendations_by_id

    pilot_rec = recommendations_by_id["shop-fast-motion-two-camera-pilot"]
    assert pilot_rec["preferred_camera_id"] == "flir-bfs-u3-16s2c-cs"
    assert pilot_rec["status"] == "provisional"

    eth_rec = recommendations_by_id["shop-distributed-ethernet-reference-evaluation"]
    assert eth_rec["preferred_camera_id"] == "allied-alvium-g5-203c"
    assert "lucid-triton2-trt016s-cc" in eth_rec["alternate_camera_ids"]
    assert eth_rec["status"] == "evaluation_only"

    assert "Allied Vision" in article
    assert "LUCID" in article
    assert "IEEE 1588" in article or "PTP" in article
    assert "5GigE" in article or "GigE" in article


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
