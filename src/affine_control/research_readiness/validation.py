"""I/O-bound validation for the research-readiness lifecycle registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

from .authority import (
    authority_ids,
    route_audits,
    validate_evidence_authority,
    validate_links,
)
from .errors import ResearchReadinessError
from .files import checked_file, digest, load_json, schema_errors
from .states import (
    REQUIRED_EVIDENCE,
    protocol_revision,
    record_revision,
    transition_allowed,
    validation_origin_allowed,
)
from .supersession import validate_supersession


@dataclass(frozen=True)
class EvidenceStatus:
    """Validated lifecycle-gate evidence metadata."""

    availability: str
    kind: str
    origin: str
    reviewed_on: date
    status: str
    status_history: tuple[tuple[date, str], ...]


def _records(library: object) -> list[dict[str, object]]:
    """Return protocol records after enforcing their container shape."""
    if not isinstance(library, dict) or not isinstance(library.get("protocols"), list):
        raise ResearchReadinessError("Library protocols must be a list")
    records = cast(list[object], library["protocols"])
    if not all(isinstance(record, dict) for record in records):
        raise ResearchReadinessError("Library protocols must be objects")
    return cast(list[dict[str, object]], records)


def _validate_public_evidence(record: dict[str, object], root: Path) -> None:
    """Validate the path and digest of public evidence."""
    path = checked_file(root, record.get("path"), "evidence path")
    if digest(path) != record.get("sha256"):
        raise ResearchReadinessError(f"Evidence digest mismatch: {record.get('path')}")


def _evidence_history(record: dict[str, object], evidence_id: str) -> tuple[tuple[date, str], ...]:
    """Validate and normalize one evidence status history."""
    history_raw = record.get("status_history", [])
    if not isinstance(history_raw, list):
        raise ResearchReadinessError(f"Evidence status history is invalid: {evidence_id}")
    status_history: list[tuple[date, str]] = []
    for event in cast(list[object], history_raw):
        if not isinstance(event, dict):
            raise ResearchReadinessError(f"Evidence status history is invalid: {evidence_id}")
        status_history.append((date.fromisoformat(str(event.get("on"))), str(event.get("status"))))
    dates = [item[0] for item in status_history]
    if status_history != sorted(status_history) or len(dates) != len(set(dates)):
        raise ResearchReadinessError(f"Evidence status history is non-monotonic: {evidence_id}")
    if status_history and status_history[-1][1] != record.get("status"):
        raise ResearchReadinessError(
            f"Evidence current status disagrees with history: {evidence_id}"
        )
    return tuple(status_history)


def _evidence_status(
    protocol: dict[str, object], record: dict[str, object], root: Path, evidence_id: str
) -> EvidenceStatus:
    """Validate one evidence record and project its lifecycle status."""
    if record.get("scope") not in {protocol["protocol_id"], "library-wide"}:
        raise ResearchReadinessError(f"Evidence scope mismatch: {evidence_id}")
    if record.get("availability") == "public":
        _validate_public_evidence(record, root)
    validate_evidence_authority(protocol, record)
    return EvidenceStatus(
        availability=str(record.get("availability")),
        kind=str(record.get("kind")),
        origin=str(record.get("evidence_origin")),
        reviewed_on=date.fromisoformat(str(record.get("reviewed_on"))),
        status=str(record.get("status")),
        status_history=_evidence_history(record, evidence_id),
    )


def _validate_evidence(
    protocol: dict[str, object], root: Path, global_ids: set[str]
) -> tuple[dict[str, EvidenceStatus], list[dict[str, object]]]:
    """Validate protocol evidence and return its gate-relevant status."""
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
        evidence[evidence_id] = _evidence_status(protocol, record, root, evidence_id)
    return evidence, cast(list[dict[str, object]], raw)


def _status_at(item: EvidenceStatus, event_on: date) -> str:
    """Return the evidence status that was in force on a lifecycle date."""
    if item.reviewed_on > event_on:
        raise ResearchReadinessError("Evidence was reviewed after transition chronology")
    if not item.status_history:
        return item.status
    applicable = [status for changed_on, status in item.status_history if changed_on <= event_on]
    return applicable[-1] if applicable else "unavailable"


def _transition_evidence(
    target: str,
    event_on: date,
    raw_ids: object,
    evidence: dict[str, EvidenceStatus],
) -> None:
    """Require eligible evidence for one lifecycle transition."""
    if not isinstance(raw_ids, list):
        raise ResearchReadinessError(f"Transition to {target} lacks evidence IDs")
    ids = [str(value) for value in raw_ids]
    if any(value not in evidence for value in ids):
        raise ResearchReadinessError(f"Transition to {target} has unknown evidence IDs")
    eligible = {
        value
        for value in ids
        if _status_at(evidence[value], event_on) == "verified"
        and evidence[value].availability in {"public", "private"}
    }
    accepted = {evidence[value].kind for value in eligible}
    required = REQUIRED_EVIDENCE[target]
    if not required.issubset(accepted):
        missing = ", ".join(sorted(required - accepted))
        raise ResearchReadinessError(
            f"Evidence was not verified at transition to {target}: {missing}"
        )
    required_ids = {value for value in eligible if evidence[value].kind in required}
    origins = {evidence[value].origin for value in required_ids}
    if not validation_origin_allowed(target, origins):
        raise ResearchReadinessError("Validated state requires measured or estimated evidence")


def _validate_history(protocol: dict[str, object], evidence: dict[str, EvidenceStatus]) -> None:
    """Validate contiguous, evidence-backed lifecycle history."""
    history = protocol.get("history")
    if not isinstance(history, list):
        raise ResearchReadinessError("Protocol history must be a list")
    previous = "concept"
    previous_on: date | None = None
    scope = str(protocol["participant_scope"])
    for event in cast(list[object], history):
        if not isinstance(event, dict):
            raise ResearchReadinessError("Protocol history events must be objects")
        source, target = str(event.get("from")), str(event.get("to"))
        event_on = date.fromisoformat(str(event.get("on")))
        if previous_on is not None and event_on < previous_on:
            raise ResearchReadinessError("Protocol history chronology is non-monotonic")
        if source != previous:
            raise ResearchReadinessError(
                f"Protocol history is non-contiguous: {previous} -> {source}"
            )
        if not transition_allowed(source, target, scope):
            raise ResearchReadinessError(f"Protocol has invalid transition: {source} -> {target}")
        _transition_evidence(target, event_on, event.get("evidence_ids"), evidence)
        if target == "published":
            raise ResearchReadinessError(
                "Published state requires external #4042 publication authority; "
                "the #4041 lifecycle cannot mint it"
            )
        previous = target
        previous_on = event_on
    if previous != protocol.get("state"):
        raise ResearchReadinessError(
            f"Protocol history does not end at state {protocol.get('state')}"
        )


def _validate_dictionary(specification: dict[str, object], root: Path) -> None:
    """Validate the exact-byte data dictionary join."""
    dictionary = specification.get("data_dictionary")
    if not isinstance(dictionary, dict):
        raise ResearchReadinessError("Protocol data dictionary must be an object")
    path = checked_file(root, dictionary.get("path"), "data dictionary")
    if digest(path) != dictionary.get("sha256"):
        raise ResearchReadinessError("Data dictionary digest mismatch")


def _validate_specification_ids(specification: dict[str, object]) -> None:
    """Require unique scientific identifiers within one specification."""
    for field, id_field in (
        ("estimands", "estimand_id"),
        ("hypotheses", "hypothesis_id"),
        ("calibrations", "calibration_id"),
    ):
        values = cast(list[dict[str, object]], specification[field])
        identifiers = [str(item[id_field]) for item in values]
        if len(identifiers) != len(set(identifiers)):
            raise ResearchReadinessError(f"duplicate IDs in {field}")


def _validate_calibrations(protocol: dict[str, object], specification: dict[str, object]) -> None:
    """Validate measurement joins, evidence origin, and verified calibrations."""
    calibrations = cast(list[dict[str, object]], specification["calibrations"])
    calibration_ids = {str(item["calibration_id"]) for item in calibrations}
    measurements = cast(list[dict[str, object]], specification["measurements"])
    quantity_classes = {str(item["quantity_class"]) for item in measurements}
    if quantity_classes != {str(protocol["evidence_origin"])}:
        raise ResearchReadinessError(
            "Protocol evidence origin and measurement quantity class differ"
        )
    for measurement in measurements:
        calibration_id = str(measurement["calibration_id"])
        if calibration_id not in calibration_ids:
            raise ResearchReadinessError(f"Measurement calibration is unknown: {calibration_id}")
    evidence = cast(list[dict[str, object]], protocol["evidence"])
    for calibration in calibrations:
        if calibration["status"] != "verified":
            continue
        calibration_id = str(calibration["calibration_id"])
        matching = [
            item
            for item in evidence
            if item.get("kind") == "calibration-record"
            and item.get("status") == "verified"
            and item.get("calibration_id") == calibration_id
        ]
        if len(matching) != 1:
            raise ResearchReadinessError(
                f"verified calibration {calibration_id} lacks matching verified evidence"
            )


def _validate_governance(protocol: dict[str, object], specification: dict[str, object]) -> None:
    """Validate participant scope against approval requirements."""
    governance = specification.get("governance")
    if not isinstance(governance, dict):
        raise ResearchReadinessError("Protocol governance must be an object")
    scope = str(protocol["participant_scope"])
    expected = {
        "human_approval_required": scope == "human",
        "animal_approval_required": scope == "animal",
        "private_data_approval_required": scope == "private-data",
    }
    if any(governance.get(field) is not required for field, required in expected.items()):
        raise ResearchReadinessError(
            f"Protocol participant scope {scope} is inconsistent with governance approvals"
        )


def _validate_specification(protocol: dict[str, object], root: Path) -> None:
    """Validate exact data-dictionary and governance specification joins."""
    specification = protocol.get("specification")
    if not isinstance(specification, dict):
        raise ResearchReadinessError("Protocol specification must be an object")
    _validate_dictionary(specification, root)
    _validate_specification_ids(specification)
    _validate_calibrations(protocol, specification)
    _validate_governance(protocol, specification)


def _validate_attempts(protocol: dict[str, object], evidence: dict[str, EvidenceStatus]) -> None:
    """Validate promotion-attempt identities and referenced evidence."""
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
        target = str(attempt.get("target"))
        current_state = str(protocol.get("state"))
        if current_state == "superseded":
            history = cast(list[dict[str, object]], protocol["history"])
            current_state = str(history[-1]["from"])
        if not transition_allowed(current_state, target, str(protocol.get("participant_scope"))):
            raise ResearchReadinessError(
                f"Promotion attempt target {target} is not structurally reachable"
            )
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
    errors = schema_errors(library, schema_path)
    if errors:
        raise ResearchReadinessError("; ".join(errors))
    records = _records(library)
    ids = [str(record["protocol_id"]) for record in records]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ResearchReadinessError("Protocol IDs must be unique and sorted")
    claims = authority_ids(claims_path, "pages", "claim_id")
    critiques = authority_ids(critiques_path, "critiques", "critique_id")
    audits = route_audits(root)
    evidence_ids: set[str] = set()
    for protocol in records:
        history = cast(list[dict[str, object]], protocol["history"])
        if protocol.get("state") == "published" or any(
            event.get("to") == "published" for event in history
        ):
            raise ResearchReadinessError(
                "Published state requires external #4042 publication authority; "
                "the #4041 lifecycle cannot mint it"
            )
        if protocol_revision(protocol) != protocol.get("protocol_revision"):
            raise ResearchReadinessError(f"protocol revision mismatch: {protocol['protocol_id']}")
        if record_revision(protocol) != protocol.get("record_revision"):
            raise ResearchReadinessError(f"record revision mismatch: {protocol['protocol_id']}")
        evidence, evidence_records = _validate_evidence(protocol, root, evidence_ids)
        _validate_history(protocol, evidence)
        _validate_attempts(protocol, evidence)
        _validate_specification(protocol, root)
        validate_links(protocol, claims, critiques, audits, evidence_records, root)
    validate_supersession(records)


def load_library(
    library_path: Path,
    schema_path: Path,
    claims_path: Path,
    critiques_path: Path,
    root: Path,
) -> dict[str, object]:
    """Load and validate the canonical readiness library."""
    library = load_json(library_path)
    validate_library(library, schema_path, claims_path, critiques_path, root)
    if not isinstance(library, dict):
        raise ResearchReadinessError("Library must be an object")
    return library
