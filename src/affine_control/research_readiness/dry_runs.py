"""Program-specific manufactured dry-run result manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .programs import PROGRAMS, ProgramSeed

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _canonical_digest(value: object) -> str:
    """Return a deterministic digest for one manufactured structure."""
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _rows(seed: ProgramSeed) -> list[dict[str, object]]:
    """Return the adverse outcome rows for one specific program."""
    protocol_id = f"ad-protocol-{seed.slug}-001"
    return [
        {
            "protocol_id": protocol_id,
            "case_id": "negative-001",
            "outcome_status": "negative",
            "value": -1.0,
        },
        {
            "protocol_id": protocol_id,
            "case_id": "null-001",
            "outcome_status": "null",
            "value": 0.0,
        },
        {
            "protocol_id": protocol_id,
            "case_id": "unavailable-001",
            "outcome_status": "unavailable",
            "value": None,
        },
    ]


def _manifest(seed: ProgramSeed, root: Path) -> dict[str, object]:
    """Build an exact input/workflow/result manifest for one program."""
    rows = _rows(seed)
    workflow = root / seed.workflow_path
    result = {
        "estimand_ids": [f"est-{seed.slug}"],
        "outcome_statuses": sorted({str(row["outcome_status"]) for row in rows}),
        "protocol_id": f"ad-protocol-{seed.slug}-001",
        "rows": rows,
    }
    return {
        "protocol_id": result["protocol_id"],
        "workflow_path": seed.workflow_path,
        "estimand_ids": result["estimand_ids"],
        "outcome_statuses": result["outcome_statuses"],
        "input_sha256": _canonical_digest(rows),
        "workflow_sha256": hashlib.sha256(workflow.read_bytes()).hexdigest(),
        "result_sha256": _canonical_digest(result),
    }


def manufactured_dictionary() -> dict[str, object]:
    """Return the shared dry-run data dictionary."""
    return {
        "schema_version": "affinedrift.research-dry-run-dictionary/v1",
        "fields": [
            {"name": "protocol_id", "type": "string", "unit": "not applicable"},
            {"name": "case_id", "type": "string", "unit": "not applicable"},
            {"name": "outcome_status", "type": "string", "unit": "not applicable"},
            {"name": "value", "type": ["number", "null"], "unit": "declared by protocol"},
        ],
        "privacy": "Manufactured records contain no participant or private data.",
    }


def manufactured_dry_runs(root: Path = REPOSITORY_ROOT) -> dict[str, object]:
    """Return deterministic program-specific negative, null, and unavailable results."""
    rows = [row for seed in PROGRAMS for row in _rows(seed)]
    manifests = [_manifest(seed, root) for seed in PROGRAMS]
    manifests.sort(key=lambda item: str(item["protocol_id"]))
    return {
        "schema_version": "affinedrift.research-dry-run/v2",
        "evidence_origin": "manufactured-synthetic",
        "authorizes_data_collection": False,
        "authorizes_claim_promotion": False,
        "protocols": manifests,
        "rows": rows,
    }
