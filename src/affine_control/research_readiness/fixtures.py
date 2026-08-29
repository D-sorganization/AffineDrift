"""Safe manufactured fixtures for the E1--E8 readiness catalog."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from .programs import PROGRAMS, ProgramSeed
from .states import protocol_revision, record_revision


def _digest(path: Path) -> str:
    """Return the SHA-256 digest of one fixture dependency."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def manufactured_dry_runs() -> dict[str, object]:
    """Return deterministic negative, null, and unavailable dry-run outcomes."""
    rows = []
    for seed in PROGRAMS:
        protocol_id = f"ad-protocol-{seed.slug}-001"
        rows.extend(
            [
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
        )
    return {
        "schema_version": "affinedrift.research-dry-run/v1",
        "evidence_origin": "manufactured-synthetic",
        "authorizes_data_collection": False,
        "authorizes_claim_promotion": False,
        "rows": rows,
    }


def _route_authority(inventory: dict[str, object], route: str) -> dict[str, object]:
    """Return the sole reviewed audit record for a public route."""
    routes = cast(list[dict[str, object]], inventory["routes"])
    matches = [record for record in routes if record.get("route") == route]
    if len(matches) != 1 or matches[0].get("status") != "reviewed":
        raise ValueError(f"Route must have exactly one reviewed audit: {route}")
    return matches[0]


def _artifact(audit: dict[str, object], prefixes: tuple[str, ...]) -> dict[str, str]:
    """Project one exact-byte artifact from a reviewed route audit."""
    review = cast(dict[str, object], audit["review"])
    digest_map = cast(dict[str, str], review["evidence_sha256"])
    paths = sorted(
        path for path in digest_map if any(path.startswith(prefix) for prefix in prefixes)
    )
    if not paths:
        raise ValueError(f"Route audit lacks {prefixes} evidence")
    path = paths[0]
    return {
        "path": path,
        "sha256": digest_map[path],
        "source_revision": str(review["review_commit"]),
        "route_audit_id": str(audit["audit_id"]),
    }


def _specification(seed: ProgramSeed, dictionary_path: Path, root: Path) -> dict[str, object]:
    """Build the non-authorizing scientific specification for one program."""
    human = seed.participant_scope == "human"
    return {
        "question": seed.question,
        "estimands": [
            {
                "estimand_id": f"est-{seed.slug}",
                "description": seed.outcome,
                "population": (
                    "Future eligible participants under approval"
                    if human
                    else "Declared modeled systems only"
                ),
                "outcome": seed.outcome,
                "contrast": seed.intervention,
            }
        ],
        "hypotheses": [
            {
                "hypothesis_id": f"hyp-{seed.slug}",
                "statement": (
                    f"The declared analysis can distinguish {seed.outcome} from its "
                    "manufactured null case."
                ),
                "direction": "two-sided",
                "falsifier": "The locked manufactured adverse or null case is promoted as support.",
                "null_handling": "Retain and report negative, null, and unavailable outcomes.",
            }
        ],
        "population": {
            "target_population": (
                "Future consenting adult golfers under separate approval"
                if human
                else "Declared analytical and simulated systems"
            ),
            "sampling_frame": "Unavailable; manufactured dry run only",
            "inclusion": [
                (
                    "Meets a future protocol-specific eligibility contract"
                    if human
                    else "Matches the declared model contract"
                )
            ],
            "exclusion": ["Undeclared frame, unit, calibration, or provenance"],
            "authority": "No population authority; no participant sample is present.",
        },
        "intervention_exposure": {
            "type": "modeled-perturbation",
            "description": seed.intervention,
            "comparator": "Locked declared baseline",
        },
        "measurements": [
            {
                "name": seed.measurement,
                "quantity_class": seed.evidence_origin,
                "frame": seed.frame,
                "unit": seed.unit,
                "calibration_id": f"cal-{seed.slug}",
            }
        ],
        "calibrations": [
            {
                "calibration_id": f"cal-{seed.slug}",
                "status": "planned",
                "plan": (
                    "Freeze traceability, range, resolution, synchronization, drift, "
                    "and acceptance limits before pilot use."
                ),
            }
        ],
        "data_dictionary": {
            "path": dictionary_path.relative_to(root).as_posix(),
            "sha256": _digest(dictionary_path),
        },
        "governance": {
            "privacy": (
                "No participant data are present; a data-minimization and access plan "
                "is required before collection."
            ),
            "license": (
                "Manufactured fixture is repository-licensed; measured-data rights "
                "are unavailable."
            ),
            "consent": (
                "Not applicable to manufactured data; human consent remains unavailable."
                if human
                else "No participants are in scope for the current modeled protocol."
            ),
            "ethics": (
                "Human review is required before pilot or collection."
                if human
                else (
                    "Validator-owned participant_scope=none; no human or animal data "
                    "are permitted."
                )
            ),
            "human_approval_required": human,
            "animal_approval_required": False,
            "private_data_approval_required": False,
        },
        "analysis": {
            "workflow_path": "scripts/generate_research_readiness_library.py",
            "power_plan": (
                "Unavailable until a pilot supplies a justified variance or precision basis."
            ),
            "exclusion_rules": [
                "Reject undeclared frames, units, calibration, or provenance",
                "Do not remove adverse or null outcomes post hoc",
            ],
            "uncertainty_plan": (
                "Propagate declared model, parameter, measurement, event-time, and "
                "sampling uncertainty; unavailable components remain unavailable."
            ),
            "falsifiers": [
                "A manufactured negative or null case is reported as confirmation",
                "A required gate is satisfied by modeled evidence outside its allowed scope",
            ],
            "null_result_policy": (
                "Retain negative, null, and unavailable outcomes in every generated view."
            ),
            "deviation_policy": (
                "Append deviations before analysis and create a new revision after a "
                "locked change."
            ),
            "promotion_criteria": [
                "Meet every target-state gate",
                "Obtain independent #4042 release evidence before publication",
                "Preserve claim, critique, and route-audit joins",
            ],
        },
    }


def _protocol(
    seed: ProgramSeed,
    audit: dict[str, object],
    schema_path: Path,
    dry_run_path: Path,
    dictionary_path: Path,
    root: Path,
) -> dict[str, object]:
    """Build one revision-bound manufactured readiness protocol."""
    protocol_id = f"ad-protocol-{seed.slug}-001"
    review = cast(dict[str, object], audit["review"])
    evidence_map = cast(dict[str, str], review["evidence_sha256"])
    source_path = str(review["source_path"])
    protocol: dict[str, object] = {
        "protocol_id": protocol_id,
        "title": seed.title,
        "companion_issue": seed.issue,
        "owner": "AffineDrift issue #4041 readiness library",
        "record_revision": "0" * 64,
        "protocol_revision": "0" * 64,
        "state": "simulation-ready",
        "participant_scope": seed.participant_scope,
        "evidence_origin": seed.evidence_origin,
        "authority_boundary": (
            "Exploratory manufactured protocol evidence only; no coaching, clinical, "
            "design, causal, population, collection, or claim-promotion authority."
        ),
        "unavailable_boundaries": [
            "Measured participant and external-site evidence",
            "Qualified instrumentation, ethics, consent, privacy, and data licenses",
            "Independent #4042 validation and publication release",
        ],
        "specification": _specification(seed, dictionary_path, root),
        "links": {
            "claim_ids": audit["claim_ids"],
            "claim_link_status": "linked" if audit["claim_ids"] else "unavailable",
            "claim_link_next_gate": (
                "Register only bounded claims through the canonical claim authority."
            ),
            "critique_ids": audit["critique_ids"],
            "critique_link_status": "linked" if audit["critique_ids"] else "unavailable",
            "critique_link_next_gate": (
                "Register critiques through the canonical adjudication ledger."
            ),
            "calculation_artifacts": [_artifact(audit, ("src/", "articles/", "models/"))],
            "workflow_artifacts": [_artifact(audit, ("tests/",))],
            "datasets": [
                {
                    "availability": "public",
                    "evidence_origin": "manufactured-synthetic",
                    "path": dry_run_path.relative_to(root).as_posix(),
                    "sha256": _digest(dry_run_path),
                }
            ],
            "route_audits": [{"audit_id": audit["audit_id"], "route": audit["route"]}],
            "validation_release": {
                "status": "unavailable",
                "next_gate": "Obtain an immutable verified #4042 release reference.",
            },
        },
        "evidence": [
            {
                "evidence_id": f"evidence-{seed.slug}-review",
                "kind": "evidence-review",
                "status": "verified",
                "scope": protocol_id,
                "availability": "public",
                "evidence_origin": seed.evidence_origin,
                "path": source_path,
                "sha256": evidence_map[source_path],
                "reviewed_by": f"AffineDrift issue #{seed.issue} protected review",
                "reviewed_on": "2026-08-29",
            },
            {
                "evidence_id": f"evidence-{seed.slug}-schema",
                "kind": "schema-validation",
                "status": "verified",
                "scope": protocol_id,
                "availability": "public",
                "evidence_origin": "manufactured-synthetic",
                "path": schema_path.relative_to(root).as_posix(),
                "sha256": _digest(schema_path),
                "reviewed_by": "AffineDrift issue #4041 executable contract",
                "reviewed_on": "2026-08-29",
            },
            {
                "evidence_id": f"evidence-{seed.slug}-dry-run",
                "kind": "synthetic-dry-run",
                "status": "verified",
                "scope": protocol_id,
                "availability": "public",
                "evidence_origin": "manufactured-synthetic",
                "path": dry_run_path.relative_to(root).as_posix(),
                "sha256": _digest(dry_run_path),
                "reviewed_by": "AffineDrift issue #4041 deterministic dry run",
                "reviewed_on": "2026-08-29",
            },
        ],
        "history": [
            {
                "from": "concept",
                "to": "evidence-reviewed",
                "on": "2026-08-29",
                "rationale": "Exact reviewed route evidence and authority boundaries are joined.",
                "evidence_ids": [f"evidence-{seed.slug}-review"],
            },
            {
                "from": "evidence-reviewed",
                "to": "simulation-ready",
                "on": "2026-08-29",
                "rationale": (
                    "The strict schema and adverse manufactured dry run validate " "mechanics only."
                ),
                "evidence_ids": [f"evidence-{seed.slug}-schema", f"evidence-{seed.slug}-dry-run"],
            },
        ],
        "promotion_attempts": [
            {
                "attempt_id": f"attempt-{seed.slug}-pilot",
                "target": "pilot-ready",
                "outcome": "rejected",
                "on": "2026-08-29",
                "rationale": (
                    "Qualified measurement, calibration, risk, power, and governance "
                    "evidence are unavailable."
                ),
                "evidence_ids": [],
            }
        ],
    }
    protocol["protocol_revision"] = protocol_revision(protocol)
    protocol["record_revision"] = record_revision(protocol)
    return protocol


def build_manufactured_library(root: Path) -> dict[str, object]:
    """Build the deterministic E1--E8 readiness registry from audited sources."""
    inventory = json.loads(
        (root / "data/trust/claim_audit_inventory.json").read_text(encoding="utf-8")
    )
    schema_path = root / "schemas/research-protocol-readiness-v1.schema.json"
    dry_run_path = root / "data/research_protocols/manufactured_dry_runs.json"
    dictionary_path = root / "data/research_protocols/data_dictionary.json"
    protocols = [
        _protocol(
            seed,
            _route_authority(inventory, seed.route),
            schema_path,
            dry_run_path,
            dictionary_path,
            root,
        )
        for seed in PROGRAMS
    ]
    protocols.sort(key=lambda record: str(record["protocol_id"]))
    return {"schema_version": "affinedrift.research-protocol-readiness/v1", "protocols": protocols}
