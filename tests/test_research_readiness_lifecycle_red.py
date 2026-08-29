"""RED contracts for chronological and revision-safe readiness history."""

from __future__ import annotations

from typing import cast

import pytest

from src.affine_control.research_readiness import ResearchReadinessError
from tests.research_readiness_test_support import (
    canonical_library,
    opaque_evidence,
    protocol,
    reseal,
    validate,
)


def test_evidence_must_be_reviewed_before_the_transition_it_authorizes() -> None:
    """Future-reviewed evidence cannot authorize an earlier lifecycle event."""
    library = canonical_library()
    record = protocol(library)
    evidence = cast(list[dict[str, object]], record["evidence"])
    evidence[0]["reviewed_on"] = "2099-01-01"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="evidence.*after transition|chronology"):
        validate(library)


def test_current_verification_cannot_retroactively_authorize_a_transition() -> None:
    """Current status cannot obscure the evidence state at promotion time."""
    library = canonical_library()
    record = protocol(library)
    evidence = cast(list[dict[str, object]], record["evidence"])
    evidence[0]["status_history"] = [
        {"status": "rejected", "on": "2026-08-28"},
        {"status": "verified", "on": "2026-08-30"},
    ]
    evidence[0]["status"] = "verified"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="not verified at transition"):
        validate(library)


def test_history_event_dates_are_monotonic() -> None:
    """A later readiness state cannot carry an earlier event date."""
    library = canonical_library()
    record = protocol(library)
    history = cast(list[dict[str, object]], record["history"])
    history[0]["on"] = "2026-08-30"
    history[1]["on"] = "2026-08-29"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="history.*chronolog|non-monotonic"):
        validate(library)


def test_rejected_attempt_target_must_be_a_structurally_reachable_next_state() -> None:
    """Rejected-attempt history cannot claim an unrelated publication attempt."""
    library = canonical_library()
    record = protocol(library)
    attempts = cast(list[dict[str, object]], record["promotion_attempts"])
    attempts[0]["target"] = "published"
    reseal(record)

    with pytest.raises(ResearchReadinessError, match="promotion attempt.*target|reachable"):
        validate(library)


def test_later_revocation_preserves_verified_transition_history_when_superseded() -> None:
    """A later revocation must not erase the status that authorized an old transition."""
    library = canonical_library()
    record = protocol(library)
    successor = protocol(library, "ad-protocol-hybrid-impact-001")
    evidence = cast(list[dict[str, object]], record["evidence"])
    history = cast(list[dict[str, object]], record["history"])
    reviewed = evidence[0]
    reviewed["status"] = "revoked"
    reviewed["status_history"] = [
        {
            "status": "verified",
            "on": "2026-08-29",
            "rationale": "Evidence was verified when the transition occurred.",
        },
        {
            "status": "revoked",
            "on": "2026-08-30",
            "rationale": "Later review withdrew the evidence.",
        },
    ]
    supersession_id = "evidence-dcr-revocation-supersession"
    supersession = opaque_evidence(record, supersession_id, "supersession-record")
    supersession["related_protocol_id"] = successor["protocol_id"]
    supersession["related_record_revision"] = successor["record_revision"]
    supersession["reviewed_on"] = "2026-08-30"
    evidence.append(supersession)
    history.append(
        {
            "from": "simulation-ready",
            "to": "superseded",
            "on": "2026-08-30",
            "rationale": "Withdraw the current protocol after evidence revocation.",
            "evidence_ids": [supersession_id],
        }
    )
    record["successor_protocol_id"] = successor["protocol_id"]
    record["state"] = "superseded"
    reseal(record)

    validate(library)
