"""I/O-bound validation for the research-readiness lifecycle registry."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from .states import (
    REQUIRED_EVIDENCE,
    protocol_revision,
    record_revision,
    transition_allowed,
    validation_origin_allowed,
)

MAX_EVIDENCE_BYTES = 5_000_000


class ResearchReadinessError(ValueError):
    """Raised when research-readiness evidence fails closed."""


@dataclass(frozen=True)
class EvidenceStatus:
    """Validated lifecycle-gate evidence metadata."""

    kind: str
    origin: str
    status: str


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ResearchReadinessError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except ResearchReadinessError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchReadinessError(f"Cannot load JSON contract {path}: {exc}") from exc


def _schema_errors(library: object, schema_path: Path) -> list[str]:
    validator = Draft202012Validator(_load_json(schema_path), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(library), key=lambda error: list(error.absolute_path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _records(library: object) -> list[dict[str, object]]:
    if not isinstance(library, dict) or not isinstance(library.get("protocols"), list):
        raise ResearchReadinessError("Library protocols must be a list")
    records = cast(list[object], library["protocols"])
    if not all(isinstance(record, dict) for record in records):
        raise ResearchReadinessError("Library protocols must be objects")
    return cast(list[dict[str, object]], records)


def _checked_file(root: Path, raw_path: object, label: str) -> Path:
    value = str(raw_path)
    parts = PurePosixPath(value).parts
    if not value or any(part in {".", ".."} for part in parts):
        raise ResearchReadinessError(f"Repository path traversal is forbidden: {value}")
    unresolved = root.joinpath(*parts)
    if unresolved.is_symlink():
        raise ResearchReadinessError(f"Symlink evidence is forbidden: {value}")
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ResearchReadinessError(f"Repository path traversal is forbidden: {value}") from exc
    if not candidate.is_file():
        raise ResearchReadinessError(f"Missing {label}: {value}")
    if candidate.stat().st_size > MAX_EVIDENCE_BYTES:
        raise ResearchReadinessError(f"Oversized {label}: {value}")
    return candidate


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _authority_ids(path: Path, collection: str, id_field: str) -> set[str]:
    document = _load_json(path)
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


def _route_audits(root: Path) -> dict[str, dict[str, object]]:
    inventory = _load_json(root / "data/trust/claim_audit_inventory.json")
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


def _validate_public_evidence(record: dict[str, object], root: Path) -> None:
    path = _checked_file(root, record.get("path"), "evidence path")
    if _digest(path) != record.get("sha256"):
        raise ResearchReadinessError(f"Evidence digest mismatch: {record.get('path')}")


def _validate_evidence(
    protocol: dict[str, object], root: Path, global_ids: set[str]
) -> dict[str, EvidenceStatus]:
    raw = protocol.get("evidence")
    if not isinstance(raw, list):
        raise ResearchReadinessError("Protocol evidence must be a list")
    evidence: dict[str, EvidenceStatus] = {}
    for record in cast(list[object], raw):
        if not isinstance(record, dict):
            raise ResearchReadinessError("Protocol evidence records must be objects")
        evidence_id = str(record.get("evidence_id", ""))
        if evidence_id in global_ids:
            raise ResearchReadinessError(f"Duplicate evidence ID: {evidence_id}")
        global_ids.add(evidence_id)
        if record.get("scope") not in {protocol["protocol_id"], "library-wide"}:
            raise ResearchReadinessError(f"Evidence scope mismatch: {evidence_id}")
        if record.get("availability") == "public":
            _validate_public_evidence(record, root)
        evidence[evidence_id] = EvidenceStatus(
            kind=str(record.get("kind")),
            origin=str(record.get("evidence_origin")),
            status=str(record.get("status")),
        )
    return evidence


def _transition_evidence(target: str, raw_ids: object, evidence: dict[str, EvidenceStatus]) -> None:
    if not isinstance(raw_ids, list):
        raise ResearchReadinessError(f"Transition to {target} lacks evidence IDs")
    ids = [str(value) for value in raw_ids]
    if any(value not in evidence for value in ids):
        raise ResearchReadinessError(f"Transition to {target} has unknown evidence IDs")
    accepted = {evidence[value].kind for value in ids if evidence[value].status == "verified"}
    required = REQUIRED_EVIDENCE[target]
    if not required.issubset(accepted):
        missing = ", ".join(sorted(required - accepted))
        raise ResearchReadinessError(f"Transition to {target} lacks {missing}")
    origins = {evidence[value].origin for value in ids}
    if not validation_origin_allowed(target, origins):
        raise ResearchReadinessError("Validated state requires measured or estimated evidence")


def _validate_history(protocol: dict[str, object], evidence: dict[str, EvidenceStatus]) -> None:
    history = protocol.get("history")
    if not isinstance(history, list):
        raise ResearchReadinessError("Protocol history must be a list")
    previous = "concept"
    scope = str(protocol["participant_scope"])
    for event in cast(list[object], history):
        if not isinstance(event, dict):
            raise ResearchReadinessError("Protocol history events must be objects")
        source, target = str(event.get("from")), str(event.get("to"))
        if source != previous:
            raise ResearchReadinessError(
                f"Protocol history is non-contiguous: {previous} -> {source}"
            )
        if not transition_allowed(source, target, scope):
            raise ResearchReadinessError(f"Protocol has invalid transition: {source} -> {target}")
        _transition_evidence(target, event.get("evidence_ids"), evidence)
        previous = target
    if previous != protocol.get("state"):
        raise ResearchReadinessError(
            f"Protocol history does not end at state {protocol.get('state')}"
        )


def _validate_artifact(
    record: dict[str, object],
    label: str,
    root: Path,
    audits: dict[str, dict[str, object]],
) -> None:
    path = _checked_file(root, record.get("path"), label)
    if _digest(path) != record.get("sha256"):
        raise ResearchReadinessError(f"{label.capitalize()} digest mismatch")
    audit = audits.get(str(record.get("route_audit_id")))
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
    links: dict[str, object], root: Path, audits: dict[str, dict[str, object]]
) -> None:
    for field, label in (
        ("calculation_artifacts", "calculation artifact"),
        ("workflow_artifacts", "workflow artifact"),
    ):
        records = links.get(field)
        if not isinstance(records, list):
            raise ResearchReadinessError(f"Protocol {field} must be a list")
        for record in cast(list[object], records):
            if not isinstance(record, dict):
                raise ResearchReadinessError(f"Protocol {label} must be an object")
            _validate_artifact(record, label, root, audits)
    datasets = links.get("datasets")
    if not isinstance(datasets, list):
        raise ResearchReadinessError("Protocol datasets must be a list")
    for dataset in cast(list[object], datasets):
        if not isinstance(dataset, dict):
            raise ResearchReadinessError("Protocol datasets must be objects")
        if dataset.get("availability") == "public":
            path = _checked_file(root, dataset.get("path"), "dataset path")
            if _digest(path) != dataset.get("sha256"):
                raise ResearchReadinessError(f"Dataset digest mismatch: {dataset.get('path')}")


def _validate_links(
    protocol: dict[str, object],
    claims: set[str],
    critiques: set[str],
    audits: dict[str, dict[str, object]],
    root: Path,
) -> None:
    links = protocol.get("links")
    if not isinstance(links, dict):
        raise ResearchReadinessError("Protocol links must be an object")
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
    route_links = links.get("route_audits")
    if not isinstance(route_links, list):
        raise ResearchReadinessError("Protocol route audits must be a list")
    for link in cast(list[object], route_links):
        if not isinstance(link, dict) or str(link.get("audit_id")) not in audits:
            raise ResearchReadinessError(f"Unknown route audit ID: {link}")
        audit = audits[str(link["audit_id"])]
        if link.get("route") != audit.get("route") or audit.get("status") != "reviewed":
            raise ResearchReadinessError(
                f"Route audit ID is stale or unreviewed: {link['audit_id']}"
            )
    _validate_artifacts(links, root, audits)


def _validate_supersession(records: list[dict[str, object]]) -> None:
    ids = {str(record["protocol_id"]) for record in records}
    successors: dict[str, str] = {}
    for record in records:
        successor = record.get("successor_protocol_id")
        if successor is None:
            continue
        source = str(record["protocol_id"])
        target = str(successor)
        if target == source or target not in ids:
            raise ResearchReadinessError(f"Invalid successor protocol ID: {target}")
        successors[source] = target
    for source in successors:
        visited = {source}
        target = successors[source]
        while target in successors:
            if target in visited:
                raise ResearchReadinessError("Supersession cycle is forbidden")
            visited.add(target)
            target = successors[target]


def _validate_specification(protocol: dict[str, object], root: Path) -> None:
    specification = protocol.get("specification")
    if not isinstance(specification, dict):
        raise ResearchReadinessError("Protocol specification must be an object")
    dictionary = specification.get("data_dictionary")
    if not isinstance(dictionary, dict):
        raise ResearchReadinessError("Protocol data dictionary must be an object")
    path = _checked_file(root, dictionary.get("path"), "data dictionary")
    if _digest(path) != dictionary.get("sha256"):
        raise ResearchReadinessError("Data dictionary digest mismatch")


def _validate_attempts(protocol: dict[str, object], evidence: dict[str, EvidenceStatus]) -> None:
    attempts = protocol.get("promotion_attempts")
    if not isinstance(attempts, list):
        raise ResearchReadinessError("Protocol promotion attempts must be a list")
    ids: set[str] = set()
    for attempt in cast(list[object], attempts):
        if not isinstance(attempt, dict):
            raise ResearchReadinessError("Protocol promotion attempts must be objects")
        attempt_id = str(attempt.get("attempt_id"))
        if attempt_id in ids:
            raise ResearchReadinessError(f"Duplicate promotion attempt ID: {attempt_id}")
        ids.add(attempt_id)
        evidence_ids = attempt.get("evidence_ids")
        if not isinstance(evidence_ids, list) or any(
            str(value) not in evidence for value in evidence_ids
        ):
            raise ResearchReadinessError(
                f"promotion attempt {attempt_id} references unknown evidence"
            )


def validate_library(
    library: object,
    schema_path: Path,
    claims_path: Path,
    critiques_path: Path,
    root: Path,
) -> None:
    """Validate schema, lifecycle, evidence, revisions, and authority joins."""
    errors = _schema_errors(library, schema_path)
    if errors:
        raise ResearchReadinessError("; ".join(errors))
    records = _records(library)
    ids = [str(record["protocol_id"]) for record in records]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ResearchReadinessError("Protocol IDs must be unique and sorted")
    claims = _authority_ids(claims_path, "pages", "claim_id")
    critiques = _authority_ids(critiques_path, "critiques", "critique_id")
    audits = _route_audits(root)
    evidence_ids: set[str] = set()
    for protocol in records:
        if protocol_revision(protocol) != protocol.get("protocol_revision"):
            raise ResearchReadinessError(f"protocol revision mismatch: {protocol['protocol_id']}")
        if record_revision(protocol) != protocol.get("record_revision"):
            raise ResearchReadinessError(f"record revision mismatch: {protocol['protocol_id']}")
        evidence = _validate_evidence(protocol, root, evidence_ids)
        _validate_history(protocol, evidence)
        _validate_attempts(protocol, evidence)
        _validate_specification(protocol, root)
        _validate_links(protocol, claims, critiques, audits, root)
    _validate_supersession(records)


def load_library(
    library_path: Path,
    schema_path: Path,
    claims_path: Path,
    critiques_path: Path,
    root: Path,
) -> dict[str, object]:
    """Load and validate the canonical readiness library."""
    library = _load_json(library_path)
    validate_library(library, schema_path, claims_path, critiques_path, root)
    if not isinstance(library, dict):
        raise ResearchReadinessError("Library must be an object")
    return library
