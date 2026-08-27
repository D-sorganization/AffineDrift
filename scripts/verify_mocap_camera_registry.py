#!/usr/bin/env python3
"""Verify the source-bounded markerless-mocap camera evidence registry."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

REGISTRY_SCHEMA_ID = "affinedrift/mocap-camera-evidence-registry/v1"
REQUIRED_PURCHASING_ATTRIBUTES = frozenset(
    {
        "data_interface",
        "lens",
        "max_frame_rate",
        "price",
        "resolution",
        "sdk",
        "sdk_license",
        "shutter_type",
        "synchronization",
        "topology_limits",
    }
)
ALLOWED_SOURCE_KINDS = frozenset(
    {
        "peer_reviewed_article",
        "vendor_license",
        "vendor_product_page",
        "vendor_technical_documentation",
    }
)
SOURCE_BACKED_CLASSES = frozenset({"peer_reviewed_observed", "vendor_spec"})
ALLOWED_EVIDENCE_CLASSES = SOURCE_BACKED_CLASSES | {"engineering_inference", "unavailable"}
ALLOWED_CAMERA_ROLES = frozenset(
    {"fast_motion_reference_candidate", "long_cable_evaluation_candidate", "research_baseline"}
)
ALLOWED_INTEGRATION_STATES = frozenset({"adapter_required", "external_service_only"})
TOP_LEVEL_KEYS = {
    "schema",
    "as_of",
    "authority",
    "review_policy",
    "sources",
    "claims",
    "cameras",
    "recommendations",
}


class CameraRegistryError(RuntimeError):
    """Raised when camera evidence violates its publication contract."""


@dataclass(frozen=True)
class CameraRegistrySummary:
    """Deterministic counts for one accepted camera registry."""

    camera_count: int
    source_count: int
    claim_count: int
    recommendation_count: int
    unavailable_claim_count: int
    procurement_approved_count: int


def _object(value: object, label: str, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraRegistryError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise CameraRegistryError(
            f"{label} fields differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return result


def _array(value: object, label: str) -> list[object]:
    if not isinstance(value, list) or not value:
        raise CameraRegistryError(f"{label} must be a non-empty array")
    return cast(list[object], value)


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CameraRegistryError(f"{label} must be a non-empty string")
    return value


def _date(value: object, label: str) -> date:
    text = _text(value, label)
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise CameraRegistryError(f"{label} must be an ISO date") from error


def _unique_texts(value: object, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise CameraRegistryError(f"{label} must be {'an' if allow_empty else 'a non-empty'} array")
    texts = [_text(item, f"{label} item") for item in cast(list[object], value)]
    if len(texts) != len(set(texts)):
        raise CameraRegistryError(f"{label} must contain unique values")
    return texts


def _verify_authority(value: object) -> None:
    authority = _object(value, "authority", {"repository", "scope", "excludes"})
    if _text(authority["repository"], "authority repository") != "D-sorganization/AffineDrift":
        raise CameraRegistryError("AffineDrift must remain the registry authority")
    _text(authority["scope"], "authority scope")
    exclusions = _unique_texts(authority["excludes"], "authority exclusions")
    required = {"capture_runtime", "procurement_approval", "reconstruction_runtime"}
    if not required.issubset(exclusions):
        raise CameraRegistryError(
            "authority exclusions must preserve runtime and procurement boundaries"
        )


def _verify_policy(value: object) -> None:
    policy = _object(
        value,
        "review policy",
        {"source_precedence", "procurement_default", "maximum_review_age_days"},
    )
    precedence = _unique_texts(policy["source_precedence"], "source precedence")
    if set(precedence) != ALLOWED_SOURCE_KINDS:
        raise CameraRegistryError("source precedence must enumerate every allowed source kind")
    if _text(policy["procurement_default"], "procurement default") != "deny":
        raise CameraRegistryError("procurement must default deny")
    age = policy["maximum_review_age_days"]
    if type(age) is not int or not 1 <= age <= 366:
        raise CameraRegistryError("maximum review age must be from 1 through 366 days")


def _verify_source(value: object, index: int, as_of: date) -> str:
    source = _object(
        value,
        f"source {index}",
        {"id", "kind", "title", "publisher", "url", "published_on", "accessed_on"},
    )
    source_id = _text(source["id"], f"source {index} id")
    kind = _text(source["kind"], f"source {source_id} kind")
    if kind not in ALLOWED_SOURCE_KINDS:
        raise CameraRegistryError(f"source {source_id} kind is unsupported")
    _text(source["title"], f"source {source_id} title")
    _text(source["publisher"], f"source {source_id} publisher")
    url = _text(source["url"], f"source {source_id} URL")
    if not url.startswith("https://"):
        raise CameraRegistryError(f"source {source_id} must use HTTPS")
    published = _text(source["published_on"], f"source {source_id} publication date")
    if published != "unavailable":
        _date(published, f"source {source_id} publication date")
    if _date(source["accessed_on"], f"source {source_id} access date") > as_of:
        raise CameraRegistryError(f"source {source_id} access date is after the registry date")
    return source_id


def _verify_sources(value: object, as_of: date) -> set[str]:
    source_ids: set[str] = set()
    for index, item in enumerate(_array(value, "sources")):
        source_id = _verify_source(item, index, as_of)
        if source_id in source_ids:
            raise CameraRegistryError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
    return source_ids


def _verify_claim_state(claim: dict[str, object], claim_id: str, sources: list[str]) -> None:
    evidence_class = _text(claim["evidence_class"], f"claim {claim_id} evidence class")
    status = _text(claim["status"], f"claim {claim_id} status")
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        raise CameraRegistryError(f"claim {claim_id} evidence class is unsupported")
    if evidence_class in SOURCE_BACKED_CLASSES and not sources:
        raise CameraRegistryError(f"source-backed claim {claim_id} requires at least one source")
    if evidence_class == "engineering_inference" and status != "provisional":
        raise CameraRegistryError(f"claim {claim_id} engineering inference must remain provisional")
    if evidence_class == "unavailable":
        if status != "unavailable" or claim["value"] is not None or sources:
            raise CameraRegistryError(
                f"claim {claim_id} unavailable claim must use null and no sources"
            )
    elif status not in {"current", "provisional"} or claim["value"] is None:
        raise CameraRegistryError(f"claim {claim_id} has an invalid status or value")


def _verify_claim(
    value: object, index: int, source_ids: set[str], as_of: date
) -> tuple[str, str, str]:
    claim = _object(
        value,
        f"claim {index}",
        {
            "id",
            "subject_id",
            "attribute",
            "value",
            "unit",
            "evidence_class",
            "status",
            "source_ids",
            "accessed_on",
            "review_due",
            "limitations",
        },
    )
    claim_id = _text(claim["id"], f"claim {index} id")
    subject_id = _text(claim["subject_id"], f"claim {claim_id} subject")
    attribute = _text(claim["attribute"], f"claim {claim_id} attribute")
    _text(claim["unit"], f"claim {claim_id} unit")
    _text(claim["limitations"], f"claim {claim_id} limitations")
    sources = _unique_texts(claim["source_ids"], f"claim {claim_id} sources", allow_empty=True)
    unknown_sources = set(sources) - source_ids
    if unknown_sources:
        raise CameraRegistryError(
            f"claim {claim_id} has unknown source ids: {sorted(unknown_sources)}"
        )
    if _date(claim["accessed_on"], f"claim {claim_id} access date") > as_of:
        raise CameraRegistryError(f"claim {claim_id} access date is after the registry date")
    if _date(claim["review_due"], f"claim {claim_id} review date") <= as_of:
        raise CameraRegistryError(f"claim {claim_id} review is due or expired")
    _verify_claim_state(claim, claim_id, sources)
    return claim_id, subject_id, attribute


def _verify_claims(
    value: object, source_ids: set[str], as_of: date
) -> tuple[dict[str, tuple[str, str]], int]:
    claims: dict[str, tuple[str, str]] = {}
    unavailable = 0
    for index, item in enumerate(_array(value, "claims")):
        claim_id, subject_id, attribute = _verify_claim(item, index, source_ids, as_of)
        if claim_id in claims:
            raise CameraRegistryError(f"duplicate claim id: {claim_id}")
        claims[claim_id] = (subject_id, attribute)
        claim = cast(dict[str, object], item)
        unavailable += int(claim["status"] == "unavailable")
    return claims, unavailable


def _verify_camera_claims(
    camera_id: str, references: list[str], claims: dict[str, tuple[str, str]]
) -> None:
    attributes: set[str] = set()
    for claim_id in references:
        if claim_id not in claims:
            raise CameraRegistryError(f"camera {camera_id} references unknown claim id: {claim_id}")
        subject_id, attribute = claims[claim_id]
        if subject_id != camera_id:
            raise CameraRegistryError(f"claim {claim_id} belongs to {subject_id}, not {camera_id}")
        attributes.add(attribute)
    if attributes != REQUIRED_PURCHASING_ATTRIBUTES:
        raise CameraRegistryError(
            f"camera {camera_id} purchasing attributes differ: "
            f"missing={sorted(REQUIRED_PURCHASING_ATTRIBUTES - attributes)}, "
            f"extra={sorted(attributes - REQUIRED_PURCHASING_ATTRIBUTES)}"
        )


def _verify_camera(value: object, index: int, claims: dict[str, tuple[str, str]]) -> str:
    camera = _object(
        value,
        f"camera {index}",
        {
            "id",
            "vendor",
            "model",
            "role",
            "color",
            "integration",
            "purchasing_claim_ids",
            "limitations",
        },
    )
    camera_id = _text(camera["id"], f"camera {index} id")
    _text(camera["vendor"], f"camera {camera_id} vendor")
    _text(camera["model"], f"camera {camera_id} model")
    _text(camera["color"], f"camera {camera_id} color")
    _text(camera["limitations"], f"camera {camera_id} limitations")
    if _text(camera["role"], f"camera {camera_id} role") not in ALLOWED_CAMERA_ROLES:
        raise CameraRegistryError(f"camera {camera_id} role is unsupported")
    if (
        _text(camera["integration"], f"camera {camera_id} integration")
        not in ALLOWED_INTEGRATION_STATES
    ):
        raise CameraRegistryError(f"camera {camera_id} integration state is unsupported")
    references = _unique_texts(camera["purchasing_claim_ids"], f"camera {camera_id} claims")
    _verify_camera_claims(camera_id, references, claims)
    return camera_id


def _verify_cameras(value: object, claims: dict[str, tuple[str, str]]) -> set[str]:
    camera_ids: set[str] = set()
    for index, item in enumerate(_array(value, "cameras")):
        camera_id = _verify_camera(item, index, claims)
        if camera_id in camera_ids:
            raise CameraRegistryError(f"duplicate camera id: {camera_id}")
        camera_ids.add(camera_id)
    return camera_ids


def _verify_recommendation(
    value: object, index: int, camera_ids: set[str], claim_ids: set[str]
) -> str:
    recommendation = _object(
        value,
        f"recommendation {index}",
        {
            "id",
            "task",
            "status",
            "preferred_camera_id",
            "alternate_camera_ids",
            "rationale_claim_ids",
            "qualification_gates",
            "decision",
            "limitations",
        },
    )
    recommendation_id = _text(recommendation["id"], f"recommendation {index} id")
    status = _text(recommendation["status"], f"recommendation {recommendation_id} status")
    if status not in {"evaluation_only", "provisional"}:
        raise CameraRegistryError(f"recommendation {recommendation_id} may not approve procurement")
    preferred = _text(recommendation["preferred_camera_id"], "preferred camera")
    alternates = _unique_texts(recommendation["alternate_camera_ids"], "alternate cameras")
    if preferred not in camera_ids or not set(alternates).issubset(camera_ids):
        raise CameraRegistryError(
            f"recommendation {recommendation_id} references an unknown camera"
        )
    if preferred in alternates:
        raise CameraRegistryError(
            f"recommendation {recommendation_id} repeats the preferred camera"
        )
    rationale = _unique_texts(recommendation["rationale_claim_ids"], "recommendation rationale")
    if not set(rationale).issubset(claim_ids):
        raise CameraRegistryError(f"recommendation {recommendation_id} references an unknown claim")
    _unique_texts(recommendation["qualification_gates"], "qualification gates")
    _text(recommendation["task"], f"recommendation {recommendation_id} task")
    _text(recommendation["decision"], f"recommendation {recommendation_id} decision")
    _text(recommendation["limitations"], f"recommendation {recommendation_id} limitations")
    return recommendation_id


def _verify_recommendations(value: object, camera_ids: set[str], claim_ids: set[str]) -> set[str]:
    recommendation_ids: set[str] = set()
    for index, item in enumerate(_array(value, "recommendations")):
        item_id = _verify_recommendation(item, index, camera_ids, claim_ids)
        if item_id in recommendation_ids:
            raise CameraRegistryError(f"duplicate recommendation id: {item_id}")
        recommendation_ids.add(item_id)
    return recommendation_ids


def verify_camera_registry(value: object) -> CameraRegistrySummary:
    """Validate one registry and return deterministic evidence counts."""

    registry = _object(value, "registry", TOP_LEVEL_KEYS)
    if _text(registry["schema"], "registry schema") != REGISTRY_SCHEMA_ID:
        raise CameraRegistryError("registry schema is unsupported")
    as_of = _date(registry["as_of"], "registry date")
    _verify_authority(registry["authority"])
    _verify_policy(registry["review_policy"])
    source_ids = _verify_sources(registry["sources"], as_of)
    claims, unavailable = _verify_claims(registry["claims"], source_ids, as_of)
    camera_ids = _verify_cameras(registry["cameras"], claims)
    recommendation_ids = _verify_recommendations(
        registry["recommendations"], camera_ids, set(claims)
    )
    return CameraRegistrySummary(
        camera_count=len(camera_ids),
        source_count=len(source_ids),
        claim_count=len(claims),
        recommendation_count=len(recommendation_ids),
        unavailable_claim_count=unavailable,
        procurement_approved_count=0,
    )


def _load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CameraRegistryError(f"cannot read registry {path}: {error}") from error


def main(argv: list[str] | None = None) -> int:
    """Run the camera registry verifier CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = verify_camera_registry(_load(args.registry))
    except CameraRegistryError as error:
        sys.stderr.write(f"CAMERA REGISTRY FAILED: {error}\n")
        return 1
    sys.stdout.write(
        "CAMERA REGISTRY PASSED: "
        f"{summary.camera_count} cameras, {summary.claim_count} claims, "
        f"{summary.unavailable_claim_count} unavailable\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
