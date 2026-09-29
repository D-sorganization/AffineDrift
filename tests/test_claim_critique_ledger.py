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

    assert statuses.count("open") == 27
    assert statuses.count("responded") == 8
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
            "commit": "1" * 40,
            "rationale": "Silent reopening is forbidden.",
        }
    ]

    with pytest.raises(LedgerContractError, match="invalid transition"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_status_history_must_be_contiguous() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "deferred"
    critique["history"] = [
        {
            "from": "open",
            "to": "responded",
            "on": "2026-08-28",
            "commit": "1" * 40,
            "rationale": "First transition.",
        },
        {
            "from": "open",
            "to": "deferred",
            "on": "2026-08-29",
            "commit": "2" * 40,
            "rationale": "Disconnected transition.",
        },
    ]

    with pytest.raises(LedgerContractError, match="non-contiguous history"):
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
        "verification_commit": "1" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "A registered test fails.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }
    with pytest.raises(LedgerContractError, match="evidence path"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_traversal_paths_fail_closed_even_when_the_target_exists() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["affected_pages"] = ["articles/../critiques/index.qmd"]

    with pytest.raises(LedgerContractError, match="path traversal"):
        validate_ledger(ledger, SCHEMA, CLAIMS)

    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "responded"
    critique["adjudication"] = {
        "rationale": "Purported response.",
        "evidence_paths": ["tests/../SPEC.md"],
        "verification_commit": "1" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "The traversal is accepted.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }

    with pytest.raises(LedgerContractError, match="path traversal"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_adjudication_rejects_a_zero_commit_sentinel() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "responded"
    critique["adjudication"] = {
        "rationale": "Purported response.",
        "evidence_paths": ["tests/test_claim_critique_ledger.py"],
        "verification_commit": "0" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "The zero sentinel is accepted.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }

    with pytest.raises(LedgerContractError, match="does not match"):
        validate_ledger(ledger, SCHEMA, CLAIMS)


def test_resolved_critique_requires_contradiction_markers() -> None:
    ledger = copy.deepcopy(_canonical())
    critique = _critiques(ledger)[0]
    critique["disposition"] = "resolved"
    critique["adjudication"] = {
        "rationale": "Purported resolution.",
        "evidence_paths": ["tests/test_claim_critique_ledger.py"],
        "verification_commit": "1" * 40,
        "verified_on": "2026-08-29",
        "reviewer": "maintainer",
        "falsifier": "The contradictory statement remains active.",
        "uncertainty": "Unknown.",
        "next_gate": "Independent review.",
    }

    with pytest.raises(LedgerContractError, match="contradiction marker"):
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
        "verification_commit": "1" * 40,
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


def test_every_critique_maps_to_every_page_whose_claim_it_targets() -> None:
    ledger = _canonical()
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claim_to_page = {
        claim["claim_id"]: page["source_path"]
        for page in claims["pages"]
        for claim in page["claims"]
    }
    critiques = _critiques(ledger)
    targeting_critiques = [c for c in critiques if c.get("related_claim_ids")]
    assert len(targeting_critiques) > 0

    for critique in targeting_critiques:
        related = critique.get("related_claim_ids")
        assert isinstance(related, list)
        affected = critique.get("affected_pages")
        assert isinstance(affected, list)
        for claim_id in related:
            page_path = claim_to_page[str(claim_id)]
            assert page_path in affected, (
                f"{critique['critique_id']} targets claim {claim_id} from {page_path}, "
                f"but {page_path} is missing from affected_pages"
            )
            slug = Path(page_path).stem
            annotation_file = ANNOTATIONS / f"{slug}.qmd"
            assert annotation_file.is_file()
            assert str(critique["critique_id"]) in annotation_file.read_text(encoding="utf-8")
            page_text = (ROOT / page_path).read_text(encoding="utf-8")
            assert (
                f"{{{{< include _generated/trust/critique-annotations/{slug}.qmd >}}}}" in page_text
            )

    # Negative test: fails closed if a registered claim's page is omitted from affected_pages
    invalid_ledger = copy.deepcopy(ledger)
    critique_with_claim = next(c for c in _critiques(invalid_ledger) if c.get("related_claim_ids"))
    # Set to a valid existing page that is NOT the claim's registered page
    critique_with_claim["affected_pages"] = ["articles/affine-nature-golf-swing.qmd"]
    with pytest.raises(LedgerContractError, match="does not include .* in affected_pages"):
        validate_ledger(invalid_ledger, SCHEMA, CLAIMS)


def test_ztcf_and_proximal_distal_pages_carry_critique_annotations() -> None:
    ledger = _canonical()
    critique_map = {str(c["critique_id"]): c for c in _critiques(ledger)}

    # ZTCF critiques must affect zero-torque-counterfactual.qmd and theory-part2.qmd
    for critique_id in (
        "crit-ztcf-identifiability",
        "crit-static-fallacy-zvcf",
        "crit-passive-overshoot-artifact",
    ):
        pages = critique_map[critique_id]["affected_pages"]
        assert isinstance(pages, list)
        assert "articles/zero-torque-counterfactual.qmd" in pages
        assert "articles/theory-part2.qmd" in pages

    # Proximal-distal critiques must affect proximal-distal-energy-transfer.qmd
    for critique_id in (
        "crit-control-causality-mechanical",
        "crit-effective-plant-fallacy",
        "crit-sequencing-lie-bracket-fallacy",
        "crit-simulation-tautology",
        "crit-stiffness-pulse-paradox",
        "crit-ztcf-identifiability",
    ):
        pages = critique_map[critique_id]["affected_pages"]
        assert isinstance(pages, list)
        assert "articles/proximal-distal-energy-transfer.qmd" in pages

    for slug in (
        "zero-torque-counterfactual",
        "theory-part2",
        "proximal-distal-energy-transfer",
    ):
        page_source = (ROOT / f"articles/{slug}.qmd").read_text(encoding="utf-8")
        assert (
            f"{{{{< include _generated/trust/critique-annotations/{slug}.qmd >}}}}" in page_source
        )
        assert (ANNOTATIONS / f"{slug}.qmd").is_file()
