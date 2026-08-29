"""Pure state, gate, and deterministic revision rules."""

from __future__ import annotations

import hashlib
import json

READINESS_STATES = (
    "concept",
    "evidence-reviewed",
    "simulation-ready",
    "pilot-ready",
    "ethics-approved",
    "data-ready",
    "preregistered",
    "collecting",
    "analysis-locked",
    "validated",
    "published",
    "superseded",
)

REQUIRED_EVIDENCE: dict[str, frozenset[str]] = {
    "evidence-reviewed": frozenset({"evidence-review"}),
    "simulation-ready": frozenset({"schema-validation", "synthetic-dry-run"}),
    "pilot-ready": frozenset({"pilot-risk-review", "calibration-plan"}),
    "ethics-approved": frozenset({"ethics-approval"}),
    "data-ready": frozenset({"data-dictionary", "privacy-license-review", "calibration-record"}),
    "preregistered": frozenset({"preregistration-record"}),
    "collecting": frozenset({"collection-release"}),
    "analysis-locked": frozenset({"analysis-lock"}),
    "validated": frozenset({"validation-release", "null-result-audit"}),
    "published": frozenset({"claim-promotion-release"}),
    "superseded": frozenset({"supersession-record"}),
}


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def protocol_revision(protocol: dict[str, object]) -> str:
    """Return the SHA-256 identity of the scientific specification only."""
    return _canonical_digest(protocol.get("specification"))


def record_revision(protocol: dict[str, object]) -> str:
    """Return the SHA-256 identity of the complete lifecycle record."""
    material = {key: value for key, value in protocol.items() if key != "record_revision"}
    return _canonical_digest(material)


def transition_allowed(source: str, target: str, participant_scope: str) -> bool:
    """Return whether a lifecycle edge is structurally permitted."""
    if source not in READINESS_STATES or target not in READINESS_STATES:
        return False
    if source == "superseded":
        return False
    if target == "superseded":
        return True
    if source == "pilot-ready":
        if participant_scope == "none":
            return target == "data-ready"
        return target == "ethics-approved"
    if source == "ethics-approved":
        return participant_scope != "none" and target == "data-ready"
    source_index = READINESS_STATES.index(source)
    if source_index + 1 >= len(READINESS_STATES):
        return False
    return target == READINESS_STATES[source_index + 1]


def validation_origin_allowed(target: str, origins: set[str]) -> bool:
    """Return whether evidence origins are eligible for a target state."""
    if target != "validated":
        return True
    return bool(origins) and origins <= {"measured", "estimated"}
