"""Contracts for the markerless-mocap camera evidence registry."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Callable
from datetime import date
from decimal import Decimal
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
TOPOLOGY_FIELDS = {
    "id",
    "subject_id",
    "manufacturer",
    "model",
    "role",
    "camera_count",
    "qualification_state",
    "claim_ids",
    "runtime_authority",
    "procurement_authority",
    "limitations",
}
TOPOLOGY_ATTRIBUTES = {
    "transport",
    "synchronization",
    "power",
    "cable_distance",
    "host_controller_topology",
    "sdk_gentl",
    "aggregate_bandwidth",
    "storage_budget",
    "thermals",
    "licensing",
    "operating_systems",
    "quote_scope",
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
    assert schema["$defs"]["price_observation"]["properties"]["region"]["enum"] == [
        "US",
        "GLOBAL",
    ]
    currency_schema = schema["$defs"]["price_observation"]["properties"]["currency"]
    assert currency_schema["oneOf"][0]["enum"] == ["USD"]
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


def test_registry_rejects_non_vendor_camera_body_price_source(
    registry: dict[str, Any],
) -> None:
    """Prevent a paper or technical page from masquerading as commercial evidence."""

    claim = next(item for item in registry["claims"] if item["id"] == "flir-camera-body-price")
    claim["source_ids"] = ["nakano-2020-openpose-multicamera"]

    with pytest.raises(CameraRegistryError, match="vendor product page"):
        verify_camera_registry(registry)


def test_registry_rejects_non_finite_camera_body_amount(registry: dict[str, Any]) -> None:
    """Prevent Infinity from satisfying the positive numeric amount contract."""

    claim = next(item for item in registry["claims"] if item["id"] == "flir-camera-body-price")
    claim["value"]["amount"] = math.inf

    with pytest.raises(CameraRegistryError, match="finite"):
        verify_camera_registry(registry)


def test_reader_does_not_rank_candidates_by_camera_body_price() -> None:
    """Keep incomplete sticker prices out of camera ranking and procurement authority."""

    article = ARTICLE_PATH.read_text(encoding="utf-8")
    normalized_article = " ".join(article.lower().split())

    assert "Camera-Body Price Observations" in article
    assert "USD 371.00" in article
    assert "USD 399.00" in article
    assert "USD 424.00" in article
    assert "Basler amount unavailable" in article
    assert "do not rank the candidates" in normalized_article
    assert "Complete qualified-topology cost remains unavailable" in article
    assert "does not authorize procurement" in article


def test_registry_types_distinct_pilot_reference_and_challenger_topology_records(
    registry: dict[str, Any],
) -> None:
    """Keep the two-camera pilot distinct from both distributed-rig hypotheses."""

    assert "topology_evaluations" in registry
    evaluations = {item["role"]: item for item in registry["topology_evaluations"]}
    claims = {claim["id"]: claim for claim in registry["claims"]}

    assert set(evaluations) == {
        "pilot_role",
        "reference_topology_role",
        "distributed_challenger_role",
    }
    assert evaluations["pilot_role"]["model"] == "BFS-U3-16S2C-CS"
    assert evaluations["pilot_role"]["camera_count"] == 2
    assert evaluations["reference_topology_role"]["model"] == "Alvium G5-203"
    assert evaluations["reference_topology_role"]["camera_count"] == 8
    assert evaluations["distributed_challenger_role"]["model"] == "TRT016S-CC"
    assert evaluations["distributed_challenger_role"]["camera_count"] == 8

    for evaluation in evaluations.values():
        assert set(evaluation) == TOPOLOGY_FIELDS
        assert evaluation["runtime_authority"] == "none"
        assert evaluation["procurement_authority"] is False
        attributes = {claims[claim_id]["attribute"] for claim_id in evaluation["claim_ids"]}
        assert attributes == TOPOLOGY_ATTRIBUTES

    summary = verify_camera_registry(registry)
    assert summary.topology_evaluation_count == 3


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["topology_evaluations"][0].update(
                runtime_authority="camera_model"
            ),
            "may not grant runtime authority",
        ),
        (
            lambda data: data["topology_evaluations"][0].update(
                procurement_authority=True
            ),
            "may not approve procurement",
        ),
        (
            lambda data: data["topology_evaluations"][0].update(camera_count=8),
            "camera count does not match",
        ),
        (
            lambda data: data["topology_evaluations"][1].update(
                qualification_state="qualified"
            ),
            "qualification state does not match",
        ),
        (
            lambda data: data["topology_evaluations"][0]["claim_ids"].pop(),
            "attributes differ",
        ),
        (
            lambda data: data["topology_evaluations"][0]["claim_ids"].__setitem__(
                0, data["topology_evaluations"][1]["claim_ids"][0]
            ),
            "belongs to",
        ),
        (
            lambda data: data["topology_evaluations"][2].update(
                role="reference_topology_role",
                camera_count=8,
                qualification_state="reference_hypothesis_unqualified",
            ),
            "duplicate topology role",
        ),
    ],
)
def test_registry_rejects_topology_authority_or_coverage_drift(
    registry: dict[str, Any], mutation: Mutation, message: str
) -> None:
    """Fail closed when a topology record crosses its evidence boundary."""

    mutation(registry)

    with pytest.raises(CameraRegistryError, match=message):
        verify_camera_registry(registry)


def test_topology_schema_types_roles_and_fail_closed_authority() -> None:
    """Keep JSON-Schema consumers aligned with the executable topology contract."""

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    definition = schema["$defs"]["topology_evaluation"]

    assert set(definition["required"]) == TOPOLOGY_FIELDS
    assert definition["properties"]["role"]["enum"] == [
        "pilot_role",
        "reference_topology_role",
        "distributed_challenger_role",
    ]
    assert definition["properties"]["runtime_authority"]["const"] == "none"
    assert definition["properties"]["procurement_authority"]["const"] is False


def test_topology_payload_and_storage_screens_are_reproducible(
    registry: dict[str, Any],
) -> None:
    """Recompute every provisional raw eight-bit topology screen."""

    claims = {claim["id"]: claim for claim in registry["claims"]}
    modes = {
        "pilot_role": (1440, 1080, Decimal("226")),
        "reference_topology_role": (1632, 1248, Decimal("225")),
        "distributed_challenger_role": (1440, 1080, Decimal("166.3")),
    }
    article = ARTICLE_PATH.read_text(encoding="utf-8")
    for evaluation in registry["topology_evaluations"]:
        width, height, frame_rate = modes[evaluation["role"]]
        bits_per_second = Decimal(evaluation["camera_count"] * width * height * 8) * frame_rate
        topology_claims = [claims[claim_id] for claim_id in evaluation["claim_ids"]]
        bandwidth = next(
            claim for claim in topology_claims if claim["attribute"] == "aggregate_bandwidth"
        )
        storage = next(
            claim for claim in topology_claims if claim["attribute"] == "storage_budget"
        )
        assert Decimal(str(bandwidth["value"])) == bits_per_second / Decimal("1e9")
        assert Decimal(str(storage["value"])) == bits_per_second / Decimal("8e6")
        assert bandwidth["status"] == "provisional"
        assert storage["status"] == "provisional"
        assert f'{bandwidth["value"]:.3f} Gbit/s' in article
        assert f'{storage["value"]:,.3f} MB/s' in article


def test_reader_separates_topology_decisions_and_preserves_qualification_boundary() -> None:
    """Require the public explanation to reject camera-body-to-rig inference."""

    normalized_article = " ".join(ARTICLE_PATH.read_text(encoding="utf-8").lower().split())

    assert "two-camera usb pilot" in normalized_article
    assert "eight-camera distributed reference-rig hypothesis" in normalized_article
    assert "ethernet/ptp challenger" in normalized_article
    assert "does not qualify the complete lab" in normalized_article
    assert "does not authorize procurement" in normalized_article
