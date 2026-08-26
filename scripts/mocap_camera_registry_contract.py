"""Shared constants and result types for the mocap camera registry contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import cast

REGISTRY_SCHEMA_ID = "affinedrift/mocap-camera-evidence-registry/v1"
REQUIRED_PURCHASING_ATTRIBUTES = frozenset(
    {
        "data_interface",
        "lens",
        "max_frame_rate",
        "camera_body_price",
        "complete_qualified_topology_cost",
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
    "topology_evaluations",
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
    topology_evaluation_count: int
    unavailable_claim_count: int
    procurement_approved_count: int


def require_object(value: object, label: str, keys: set[str]) -> dict[str, object]:
    """Return an exact-key object or fail closed."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraRegistryError(f"{label} must be an object")
    result = cast(dict[str, object], value)
    actual = set(result)
    if actual != keys:
        raise CameraRegistryError(
            f"{label} fields differ: missing={sorted(keys - actual)}, "
            f"extra={sorted(actual - keys)}"
        )
    return result


def require_array(value: object, label: str) -> list[object]:
    """Return a non-empty array or fail closed."""

    if not isinstance(value, list) or not value:
        raise CameraRegistryError(f"{label} must be a non-empty array")
    return cast(list[object], value)


def require_text(value: object, label: str) -> str:
    """Return non-blank text or fail closed."""

    if not isinstance(value, str) or not value.strip():
        raise CameraRegistryError(f"{label} must be a non-empty string")
    return value


def require_date(value: object, label: str) -> date:
    """Return an ISO date or fail closed."""

    text = require_text(value, label)
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise CameraRegistryError(f"{label} must be an ISO date") from error


def require_unique_texts(
    value: object, label: str, *, allow_empty: bool = False
) -> list[str]:
    """Return unique non-blank strings or fail closed."""

    if not isinstance(value, list) or (not value and not allow_empty):
        article = "an" if allow_empty else "a non-empty"
        raise CameraRegistryError(f"{label} must be {article} array")
    texts = [require_text(item, f"{label} item") for item in cast(list[object], value)]
    if len(texts) != len(set(texts)):
        raise CameraRegistryError(f"{label} must contain unique values")
    return texts
