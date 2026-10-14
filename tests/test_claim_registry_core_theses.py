"""Contracts for the core-theses claims registered in the claim registry (#4522)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/trust/claim_registry.json"

REQUIRED_NONEMPTY_LIST_FIELDS = ("falsifiers", "limitations")
REQUIRED_NONEMPTY_STRING_FIELDS = ("evidence_class", "next_validation_gate")


def _claims() -> list[dict[str, object]]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pages = registry["pages"]
    assert isinstance(pages, list)
    claims: list[dict[str, object]] = []
    for page in pages:
        assert isinstance(page, dict)
        page_claims = page["claims"]
        assert isinstance(page_claims, list)
        for claim in page_claims:
            assert isinstance(claim, dict)
            claims.append(claim)
    return claims


def test_registry_contains_at_least_twelve_core_claims() -> None:
    claims = _claims()
    claim_ids = [str(claim["claim_id"]) for claim in claims]

    assert len(claims) >= 12
    assert len(claim_ids) == len(set(claim_ids)), "claim IDs must be unique"


def test_every_claim_declares_nonempty_falsifiers_and_limitations() -> None:
    for claim in _claims():
        claim_id = claim["claim_id"]
        for field in REQUIRED_NONEMPTY_LIST_FIELDS:
            value = claim.get(field)
            assert isinstance(value, list) and value, f"{claim_id} has an empty {field} list"
            assert all(
                isinstance(item, str) and item.strip() for item in value
            ), f"{claim_id} has a blank entry in {field}"


def test_every_claim_declares_its_evidence_rung_and_next_validation_gate() -> None:
    for claim in _claims():
        claim_id = claim["claim_id"]
        for field in REQUIRED_NONEMPTY_STRING_FIELDS:
            value = claim.get(field)
            assert isinstance(value, str) and value.strip(), f"{claim_id} has an empty {field}"


def test_core_theses_from_4522_are_registered() -> None:
    claim_ids = {str(claim["claim_id"]) for claim in _claims()}

    assert claim_ids == {
        "ad-dcr-001",
        "ad-decomp-001",
        "ad-ztcf-001",
        "ad-zvcf-001",
        "ad-dcr-002",
        "ad-superpos-001",
        "ad-pds-001",
        "ad-icc-001",
        "ad-sas-001",
        "ad-wuj-001",
        "ad-tsc-001",
        "ad-impact-001",
    }
