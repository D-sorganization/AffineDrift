"""Shared mutation helpers for research-readiness contract tests."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import cast

from src.affine_control.research_readiness import (
    load_library,
    protocol_revision,
    record_revision,
    validate_library,
)

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "research_protocols" / "library.json"
SCHEMA = ROOT / "schemas" / "research-protocol-readiness-v1.schema.json"
CLAIMS = ROOT / "data" / "trust" / "claim_registry.json"
CRITIQUES = ROOT / "data" / "trust" / "claim_critique_ledger.json"


def canonical_library() -> dict[str, object]:
    """Return an independently loaded, validated library for mutation."""
    return copy.deepcopy(load_library(LIBRARY, SCHEMA, CLAIMS, CRITIQUES, ROOT))


def protocol(
    library: dict[str, object],
    protocol_id: str = "ad-protocol-dcr-perturbation-001",
) -> dict[str, object]:
    """Return exactly one protocol by governed identifier."""
    records = cast(list[dict[str, object]], library["protocols"])
    matches = [record for record in records if record["protocol_id"] == protocol_id]
    assert len(matches) == 1
    return matches[0]


def specification(record: dict[str, object]) -> dict[str, object]:
    """Return a protocol's scientific specification."""
    return cast(dict[str, object], record["specification"])


def links(record: dict[str, object]) -> dict[str, object]:
    """Return a protocol's governed authority links."""
    return cast(dict[str, object], record["links"])


def reseal(record: dict[str, object], *, scientific_change: bool = False) -> None:
    """Recompute declared revisions after an intentional test mutation."""
    if scientific_change:
        record["protocol_revision"] = protocol_revision(record)
    record["record_revision"] = record_revision(record)


def validate(library: dict[str, object]) -> None:
    """Validate a mutated library against every governed dependency."""
    validate_library(library, SCHEMA, CLAIMS, CRITIQUES, ROOT)


def opaque_evidence(record: dict[str, object], evidence_id: str, kind: str) -> dict[str, object]:
    """Build deliberately self-declared opaque evidence for adversarial tests."""
    return {
        "evidence_id": evidence_id,
        "kind": kind,
        "status": "verified",
        "scope": record["protocol_id"],
        "availability": "private",
        "evidence_origin": "assumed",
        "governed_record_id": f"self-declared-{kind}",
        "record_revision": "1" * 64,
        "custodian": record["owner"],
        "disclosure_boundary": "No independent authority is present.",
        "reviewed_by": record["owner"],
        "reviewed_on": "2026-08-29",
    }
