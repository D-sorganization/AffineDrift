"""Privacy-minimized public projection for research readiness."""

from __future__ import annotations

from typing import cast

from .states import READINESS_STATES


def _records(library: object) -> list[dict[str, object]]:
    if not isinstance(library, dict) or not isinstance(library.get("protocols"), list):
        raise ValueError("Library protocols must be a list")
    return cast(list[dict[str, object]], library["protocols"])


def build_public_summary(library: object) -> dict[str, object]:
    """Build a deterministic summary with no evidence-custody details."""
    summaries: list[dict[str, object]] = []
    for protocol in _records(library):
        state = str(protocol["state"])
        index = READINESS_STATES.index(state)
        next_gate = READINESS_STATES[index + 1] if index + 1 < len(READINESS_STATES) else None
        if state == "pilot-ready" and protocol["participant_scope"] == "none":
            next_gate = "data-ready"
        summaries.append(
            {
                "authority_boundary": protocol["authority_boundary"],
                "authorizes_claim_promotion": False,
                "authorizes_data_collection": False,
                "companion_issue": protocol["companion_issue"],
                "evidence_origin": protocol["evidence_origin"],
                "next_gate": next_gate,
                "protocol_id": protocol["protocol_id"],
                "protocol_revision": protocol["protocol_revision"],
                "record_revision": protocol["record_revision"],
                "state": state,
                "title": protocol["title"],
                "unavailable_boundaries": protocol["unavailable_boundaries"],
            }
        )
    summaries.sort(key=lambda item: str(item["protocol_id"]))
    return {
        "authorizes_claim_promotion": False,
        "authorizes_data_collection": False,
        "protocols": summaries,
        "schema_version": "affinedrift.research-protocol-summary/v1",
    }
