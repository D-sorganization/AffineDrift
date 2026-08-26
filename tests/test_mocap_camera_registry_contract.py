"""Contracts for the markerless-mocap camera evidence registry."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from datetime import date
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
PRICE_FIELDS = {
    "amount",
    "currency",
    "region",
    "sku",
    "configuration",
    "price_scope",
    "tax_status",
    "shipping_status",
    "availability",
}
CAMERA_BODY_PRICE_IDS = {
    "flir-camera-body-price": {
        "amount": 371.0,
        "currency": "USD",
        "region": "US",
        "sku": "BFS-U3-16S2C-CS",
        "availability": "in_production",
    },
    "basler-camera-body-price": {
        "amount": None,
        "currency": None,
        "region": "US",
        "sku": "107821",
        "availability": "online_shop_price_not_exposed",
    },
    "zed-camera-body-base-price": {
        "amount": 399.0,
        "currency": "USD",
        "region": "GLOBAL",
        "sku": None,
        "availability": "dispatch_estimate_published",
    },
    "zed-camera-body-wide-price": {
        "amount": 424.0,
        "currency": "USD",
        "region": "GLOBAL",
        "sku": "ZED-412010",
        "availability": "dispatch_estimate_published",
    },
}
PRICE_SOURCE_HOSTS = {
    "basler-camera-body-price": "www.baslerweb.com",
    "flir-camera-body-price": "www.teledynevisionsolutions.com",
    "zed-camera-body-base-price": "store.stereolabs.com",
    "zed-camera-body-wide-price": "store.stereolabs.com",
}


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
    assert set(schema["$defs"]["price_observation"]["required"]) == PRICE_FIELDS
    assert "Provisional Shop Recommendation" in article
    assert "buy two cameras for the pilot" in article
    assert "Camera Evidence Registry" in spec
    assert "AffineDrift #3956" in handoff


def test_camera_body_prices_are_typed_scoped_primary_observations(
    registry: dict[str, Any],
) -> None:
    """Keep list-price observations configuration-specific and non-authoritative."""

    claims = {claim["id"]: claim for claim in registry["claims"]}
    sources = {source["id"]: source for source in registry["sources"]}

    for claim_id, expected in CAMERA_BODY_PRICE_IDS.items():
        claim = claims[claim_id]
        value = claim["value"]
        assert set(value) == PRICE_FIELDS
        assert value["price_scope"] == "camera_body_only"
        assert value["tax_status"] == "not_established"
        assert value["shipping_status"] == "not_established"
        for field, expected_value in expected.items():
            assert value[field] == expected_value
        assert claim["accessed_on"] == registry["as_of"]
        review_age = date.fromisoformat(claim["review_due"]) - date.fromisoformat(
            claim["accessed_on"]
        )
        assert review_age.days <= 31
        assert len(claim["source_ids"]) == 1
        source = sources[claim["source_ids"][0]]
        assert source["kind"] == "vendor_product_page"
        assert PRICE_SOURCE_HOSTS[claim_id] in source["url"]


def test_complete_topology_costs_remain_typed_and_unavailable(
    registry: dict[str, Any],
) -> None:
    """Reject a camera-body sticker price as a complete qualified-system cost."""

    cameras = {camera["id"]: camera for camera in registry["cameras"]}
    claims = {claim["id"]: claim for claim in registry["claims"]}
    complete_cost_ids = {
        "basler-complete-qualified-topology-cost",
        "flir-complete-qualified-topology-cost",
        "zed-complete-qualified-topology-cost",
    }

    for claim_id in complete_cost_ids:
        claim = claims[claim_id]
        value = claim["value"]
        assert set(value) == PRICE_FIELDS
        assert value["amount"] is None
        assert value["currency"] is None
        assert value["sku"] is None
        assert value["price_scope"] == "complete_qualified_topology"
        assert value["availability"] == "quote_required"
        assert claim["evidence_class"] == "unavailable"
        assert claim["status"] == "unavailable"
        assert claim["source_ids"] == []

    for camera in cameras.values():
        attributes = {
            claims[claim_id]["attribute"] for claim_id in camera["purchasing_claim_ids"]
        }
        assert "camera_body_price" in attributes
        assert "complete_qualified_topology_cost" in attributes

    price_claim_ids = {
        claim_id
        for claim_id, claim in claims.items()
        if claim["attribute"] in {"camera_body_price", "complete_qualified_topology_cost"}
    }
    for recommendation in registry["recommendations"]:
        assert price_claim_ids.isdisjoint(recommendation["rationale_claim_ids"])


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("currency", "usd", "currency"),
        ("region", "United States", "region"),
        ("price_scope", "complete_rig", "price scope"),
        ("tax_status", "probably excluded", "tax status"),
        ("shipping_status", "free", "shipping status"),
        ("availability", "available", "availability"),
    ],
)
def test_registry_rejects_untyped_price_metadata(
    registry: dict[str, Any], field: str, value: str, message: str
) -> None:
    """Fail closed when volatile price metadata loses its declared vocabulary."""

    claim = next(item for item in registry["claims"] if item["id"] == "flir-camera-body-price")
    claim["value"][field] = value

    with pytest.raises(CameraRegistryError, match=message):
        verify_camera_registry(registry)


def test_reader_does_not_rank_candidates_by_camera_body_price() -> None:
    """Keep incomplete sticker prices out of camera ranking and procurement authority."""

    article = ARTICLE_PATH.read_text(encoding="utf-8")

    assert "Camera-Body Price Observations" in article
    assert "USD 371.00" in article
    assert "USD 399.00" in article
    assert "USD 424.00" in article
    assert "Basler amount unavailable" in article
    assert "do not rank the candidates" in article
    assert "Complete qualified-topology cost remains unavailable" in article
    assert "does not authorize procurement" in article
