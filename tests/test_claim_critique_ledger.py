"""Contracts for the governed claim and critique adjudication ledger."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.generate_claim_critique_ledger import (
    LedgerContractError,
    generate,
    load_ledger,
    normalized_status,
    validate_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/trust/claim_critique_ledger.json"
SCHEMA = ROOT / "schemas/claim-critique-ledger-v1.schema.json"
CLAIMS = ROOT / "data/trust/claim_registry.json"
CRITIQUE_STATUS = ROOT / "critiques/_generated/critique-status.qmd"
DEFENSE = ROOT / "critiques/DEFENSE_STRATEGY.md"
SEARCH = ROOT / "data/trust/generated/claim_critique_search.json"
ANNOTATIONS = ROOT / "articles/_generated/trust/critique-annotations"


def _canonical() -> dict[str, object]:
    return load_ledger(LEDGER, SCHEMA, CLAIMS)


def _critiques(ledger: dict[str, object]) -> list[dict[str, object]]:
    critiques = ledger["critiques"]
    assert isinstance(critiques, list)
    assert all(isinstance(item, dict) for item in critiques)
    return [item for item in critiques if isinstance(item, dict)]


def test_ledger_schema_is_strict_and_versioned() -> None:
    ledger = _canonical()
    assert ledger["schema_version"] == "1.0.0"

    invalid = copy.deepcopy(ledger)
    invalid["undeclared"] = True
    with pytest.raises(LedgerContractError, match="Additional properties"):
        validate_ledger(invalid, SCHEMA, CLAIMS)


def test_every_public_critique_has_exactly_one_ledger_record() -> None:
    governed = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "critiques").glob("*.md")
        if "-bibliography" not in path.name
        and path.name not in {"DEFENSE_STRATEGY.md", "INLINE_SUGGESTIONS.md"}
    }
    registered = {str(item["source_path"]) for item in _critiques(_canonical())}

    assert len(governed) == 35
    assert registered == governed


def test_canonical_statuses_do_not_overstate_adjudication() -> None:
    statuses = [normalized_status(str(item["disposition"])) for item in _critiques(_canonical())]

    assert statuses.count("open") == 33
    assert statuses.count("responded") == 2
    assert statuses.count("resolved") == 0
    assert statuses.count("rejected") == 0


def test_unknown_disposition_defaults_to_open() -> None:
    assert normalized_status("unknown") == "open"
    assert normalized_status("open") == "open"


@pytest.mark.parametrize("status", ("responded", "resolved", "rejected"))
def test_adjudicated_status_requires_verifiable_evidence(status: str) -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = status
    critique.pop("adjudication", None)

    with pytest.raises(LedgerContractError, match="adjudication evidence"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_invalid_status_transition_fails_closed() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "open"
    critique["history"] = [
        {
            "from": "resolved",
            "to": "open",
            "on": "2026-08-29",
            "commit": "0" * 40,
            "rationale": "Silent reopening is forbidden.",
        }
    ]

    with pytest.raises(LedgerContractError, match="invalid transition"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_dangling_page_claim_and_evidence_paths_fail_closed() -> None:
    for key, value, message in (
        ("affected_pages", ["articles/missing.qmd"], "affected page"),
        ("related_claim_ids", ["ad-missing-999"], "claim ID"),
    ):
        ledger = copy.deepcopy(_canonical())
        critique = _critiques(ledger)[0]
        critique[key] = value
        with pytest.raises(LedgerContractError, match=message):
            validate_ledger(ledger, SCHEMA, CLAIMS)

    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "responded"
    critique["adjudication"] = {
        "rationale": "Purported response.",
        "evidence_paths": ["tests/missing.py"],
        "verification_commit": "0" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "A registered test fails.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }
    with pytest.raises(LedgerContractError, match="evidence path"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_resolved_critique_cannot_leave_a_contradictory_statement_active() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    page = str(critique["affected_pages"][0])  # type: ignore[index]
    active_text = (ROOT / page).read_text(encoding="utf-8").splitlines()[0]
    critique["disposition"] = "resolved"
    critique["contradiction_markers"] = [active_text]
    critique["adjudication"] = {
        "rationale": "Purported resolution.",
        "evidence_paths": ["tests/test_claim_critique_ledger.py"],
        "verification_commit": "0" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "The forbidden statement remains active.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }

    with pytest.raises(LedgerContractError, match="contradictory active statement"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_generated_ledger_surfaces_are_current_and_deterministic() -> None:
    first = generate(LEDGER, SCHEMA, CLAIMS, ROOT, check=True)
    second = generate(LEDGER, SCHEMA, CLAIMS, ROOT, check=True)

    assert first == second
    assert CRITIQUE_STATUS in first
    assert DEFENSE in first
    assert SEARCH in first


def test_generated_surfaces_expose_status_provenance_and_open_defaults() -> None:
    status = CRITIQUE_STATUS.read_text(encoding="utf-8")
    defense = DEFENSE.read_text(encoding="utf-8")
    search = json.loads(SEARCH.read_text(encoding="utf-8"))

    assert "DO NOT EDIT" in status
    assert "DO NOT EDIT" in defense
    assert defense.startswith('---\ntitle: "AffineDrift Critique Adjudication Status"')
    assert "\n## AffineDrift Critique Adjudication Status\n" in defense
    assert "\n# AffineDrift Critique Adjudication Status\n" not in defense
    assert "Open" in status
    assert "Affected Pages" in status
    assert "Verification" in status
    assert "Skeletal Baseline&quot;" in status
    assert "Theory Part 3" in status
    assert "Theory Part3" not in status
    assert ";  |" not in defense
    assert len(search["records"]) >= 36  # 35 critiques plus governed claims.
    assert "{{< include _generated/critique-status.qmd >}}" in (
        ROOT / "critiques/index.qmd"
    ).read_text(encoding="utf-8")


def test_every_affected_page_includes_its_generated_annotation() -> None:
    ledger = _canonical()
    affected: set[object] = set()
    for critique in _critiques(ledger):
        pages = critique["affected_pages"]
        assert isinstance(pages, list)
        affected.update(pages)
    for page in affected:
        source = (ROOT / str(page)).read_text(encoding="utf-8")
        slug = Path(str(page)).stem
        include = f"{{{{< include _generated/trust/critique-annotations/{slug}.qmd >}}}}"
        assert include in source
        assert (ANNOTATIONS / f"{slug}.qmd").is_file()
