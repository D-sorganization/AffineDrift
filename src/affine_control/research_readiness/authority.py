"""Governed authority, route-audit, and artifact joins for readiness records."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from .errors import ResearchReadinessError
from .files import checked_file, digest, load_json

GOVERNED_EVIDENCE_ROLES: dict[str, frozenset[str]] = {
    "independent-ethics-review": frozenset({"ethics-approval"}),
    "independent-risk-review": frozenset({"pilot-risk-review"}),
    "qualified-calibration-review": frozenset({"calibration-plan", "calibration-record"}),
    "governed-data-review": frozenset(
        {"data-dictionary", "privacy-license-review", "collection-release"}
    ),
    "independent-validation-review": frozenset(
        {"analysis-lock", "validation-release", "null-result-audit"}
    ),
}


def authority_ids(path: Path, collection: str, id_field: str) -> set[str]:
    """Load the unique identifiers exposed by one governed authority."""
    document = load_json(path)
    if not isinstance(document, dict) or not isinstance(document.get(collection), list):
        raise ResearchReadinessError(f"Authority {collection} must be a list")
    records = cast(list[object], document[collection])
    candidates: list[dict[str, object]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ResearchReadinessError(f"Authority {collection} records must be objects")
        if collection == "pages":
            claims = record.get("claims")
            if not isinstance(claims, list) or not all(isinstance(item, dict) for item in claims):
                raise ResearchReadinessError("Claim authority page is invalid")
            candidates.extend(cast(list[dict[str, object]], claims))
        else:
            candidates.append(record)
    values = [str(candidate.get(id_field, "")) for candidate in candidates]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ResearchReadinessError(f"Duplicate or empty authority ID in {collection}")
    return set(values)


def route_audits(root: Path) -> dict[str, dict[str, object]]:
    """Index the canonical route-audit authority by audit identifier."""
    inventory = load_json(root / "data/trust/claim_audit_inventory.json")
    if not isinstance(inventory, dict) or not isinstance(inventory.get("routes"), list):
        raise ResearchReadinessError("Route-audit authority is invalid")
    result: dict[str, dict[str, object]] = {}
    for record in cast(list[object], inventory["routes"]):
        if not isinstance(record, dict):
            raise ResearchReadinessError("Route-audit records must be objects")
        audit_id = str(record.get("audit_id", ""))
        if not audit_id or audit_id in result:
            raise ResearchReadinessError(f"Duplicate or empty route audit ID: {audit_id}")
        result[audit_id] = record
    return result


def validate_evidence_authority(protocol: dict[str, object], record: dict[str, object]) -> None:
    """Require independent governed roles for authority-bearing evidence kinds."""
    kind = str(record.get("kind"))
    applicable = {role for role, kinds in GOVERNED_EVIDENCE_ROLES.items() if kind in kinds}
    if not applicable:
        return
    role = str(record.get("authority_role", ""))
    authority_id = str(record.get("authority_id", ""))
    owner = str(protocol.get("owner"))
    if (
        role not in applicable
        or not authority_id.startswith("authority-")
        or record.get("reviewed_by") == owner
        or record.get("custodian") == owner
        or "self-declared" in str(record.get("governed_record_id", ""))
    ):
        raise ResearchReadinessError(
            f"Evidence {record.get('evidence_id')} lacks independent governed authority"
        )


def _validate_artifact(
    record: dict[str, object],
    label: str,
    expected_role: str,
    root: Path,
    audits: dict[str, dict[str, object]],
    declared_audits: set[str],
) -> None:
    """Validate an artifact against its file, role, and declared route audit."""
    if record.get("role") != expected_role:
        raise ResearchReadinessError(f"{label} role is invalid")
    audit_id = str(record.get("route_audit_id"))
    if audit_id not in declared_audits:
        raise ResearchReadinessError(f"{label.capitalize()} lacks a declared route audit")
    path = checked_file(root, record.get("path"), label)
    if digest(path) != record.get("sha256"):
        raise ResearchReadinessError(f"{label.capitalize()} digest mismatch")
    audit = audits.get(audit_id)
    review = audit.get("review") if isinstance(audit, dict) else None
    if not isinstance(review, dict):
        raise ResearchReadinessError(f"{label.capitalize()} lacks a reviewed route audit")
    digest_map = review.get("evidence_sha256")
    if (
        not isinstance(digest_map, dict)
        or digest_map.get(record.get("path")) != record.get("sha256")
        or review.get("review_commit") != record.get("source_revision")
    ):
        raise ResearchReadinessError(f"{label.capitalize()} is not exact-byte audit joined")


def _validate_artifacts(
    links: dict[str, object],
    root: Path,
    audits: dict[str, dict[str, object]],
    declared_audits: set[str],
) -> None:
    """Validate calculation, workflow, and dataset artifact joins."""
    for field, label, role in (
        ("calculation_artifacts", "calculation artifact", "calculation"),
        ("workflow_artifacts", "workflow artifact", "workflow"),
    ):
        records = links.get(field)
        if not isinstance(records, list):
            raise ResearchReadinessError(f"Protocol {field} must be a list")
        for record in cast(list[object], records):
            if not isinstance(record, dict):
                raise ResearchReadinessError(f"Protocol {label} must be an object")
            _validate_artifact(record, label, role, root, audits, declared_audits)
    datasets = links.get("datasets")
    if not isinstance(datasets, list):
        raise ResearchReadinessError("Protocol datasets must be a list")
    for dataset in cast(list[object], datasets):
        if not isinstance(dataset, dict):
            raise ResearchReadinessError("Protocol datasets must be objects")
        if dataset.get("availability") == "public":
            path = checked_file(root, dataset.get("path"), "dataset path")
            if digest(path) != dataset.get("sha256"):
                raise ResearchReadinessError(f"Dataset digest mismatch: {dataset.get('path')}")


def _validate_registry_links(
    links: dict[str, object], claims: set[str], critiques: set[str]
) -> None:
    """Validate claim and critique authority identifiers and link states."""
    for field, authority, label in (
        ("claim_ids", claims, "claim ID"),
        ("critique_ids", critiques, "critique ID"),
    ):
        values = links.get(field)
        if not isinstance(values, list):
            raise ResearchReadinessError(f"Protocol {field} must be a list")
        dangling = sorted(str(value) for value in values if str(value) not in authority)
        if dangling:
            raise ResearchReadinessError(f"Unknown {label}: {dangling[0]}")
        status = links.get(field.replace("_ids", "_link_status"))
        if (status == "linked") != bool(values):
            raise ResearchReadinessError(f"{label.capitalize()} availability is inconsistent")


def _declared_route_audits(
    links: dict[str, object], audits: dict[str, dict[str, object]]
) -> set[str]:
    """Validate route-audit links and return their unique identifiers."""
    route_links = links.get("route_audits")
    if not isinstance(route_links, list):
        raise ResearchReadinessError("Protocol route audits must be a list")
    declared: set[str] = set()
    for link in cast(list[object], route_links):
        if not isinstance(link, dict) or str(link.get("audit_id")) not in audits:
            raise ResearchReadinessError(f"Unknown route audit ID: {link}")
        audit_id = str(link["audit_id"])
        if audit_id in declared:
            raise ResearchReadinessError(f"duplicate route audit ID: {audit_id}")
        declared.add(audit_id)
        audit = audits[audit_id]
        if link.get("route") != audit.get("route") or audit.get("status") != "reviewed":
            raise ResearchReadinessError(f"Route audit ID is stale or unreviewed: {audit_id}")
    return declared


def _validate_release(
    links: dict[str, object], state: str, evidence: list[dict[str, object]]
) -> None:
    """Validate a verified release against lifecycle state and exact evidence."""
    release = links.get("validation_release")
    if not isinstance(release, dict):
        raise ResearchReadinessError("Protocol validation release must be an object")
    if release.get("status") != "verified":
        return
    if state not in {"validated", "published", "superseded"}:
        raise ResearchReadinessError("Verified validation release is inconsistent with state")
    matching = [
        item
        for item in evidence
        if item.get("kind") == "validation-release"
        and item.get("status") == "verified"
        and item.get("governed_record_id") == release.get("release_id")
        and item.get("record_revision") == release.get("record_revision")
    ]
    if len(matching) != 1:
        raise ResearchReadinessError("Verified validation release lacks exact release evidence")


def validate_links(
    protocol: dict[str, object],
    claims: set[str],
    critiques: set[str],
    audits: dict[str, dict[str, object]],
    evidence: list[dict[str, object]],
    root: Path,
) -> None:
    """Validate all external authority and artifact links for a protocol."""
    links = protocol.get("links")
    if not isinstance(links, dict):
        raise ResearchReadinessError("Protocol links must be an object")
    _validate_registry_links(links, claims, critiques)
    declared = _declared_route_audits(links, audits)
    _validate_artifacts(links, root, audits, declared)
    _validate_release(links, str(protocol.get("state")), evidence)
