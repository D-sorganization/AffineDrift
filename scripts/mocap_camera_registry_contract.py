"""Shared constants and result types for the mocap camera registry contract."""

from __future__ import annotations

from dataclasses import dataclass

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
