"""Contracts for the unpublished owner-review claim drafts of issue #4522.

The drafts live in ``data/trust/claim_registry_drafts_4522.json`` and are kept
out of the canonical ``data/trust/claim_registry.json`` until the owner signs
off each claim. The trust schema has no owner sign-off field, so the sign-off
state is held in a sidecar ``review_records`` list beside a schema-valid
``registry`` object. These tests pin four properties:

* every draft validates against ``schemas/trust-metadata-v1.schema.json`` with
  the same semantic checks (non-amplification, unique ids) as the live registry;
* every software-provenance path exists in this checkout;
* every claim's sign-off is pending, never approved, and cites a real heading
  in its source article;
* nothing on the publish path reads the drafts or renders a draft claim.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from scripts.generate_trust_panels import load_registry, validate_registry
from src.tools.utils.evidence_ladder import CANONICAL_RUNGS

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "data/trust/claim_registry_drafts_4522.json"
REGISTRY = ROOT / "data/trust/claim_registry.json"
SCHEMA = ROOT / "schemas/trust-metadata-v1.schema.json"
DRAFTS_NAME = DRAFTS.name

REQUIRED_TOPICS = frozenset(
    {
        "drift-control-decomposition",
        "ztcf-attribution",
        "zvcf",
        "dcr-interpretation",
        "superposition-limits",
        "proximal-distal-sequencing",
        "intentional-constraint-collapse",
        "secondary-axis-stability",
        "wrist-universal-joint-torque-transmission",
        "tangent-space-contraction",
    }
)
EVIDENCE_BASES = frozenset(
    {
        # The article derives the statement and an executable check in this
        # repository exercises the same mathematics.
        "derived-and-executable-check",
        # The article derives the statement; no dedicated regression of that
        # exact statement was located.
        "derived-in-article-only",
        # The article reports a model result produced elsewhere; this
        # repository holds only a pinned snapshot and its integrity checker.
        "reported-snapshot",
        # The article only asserts or proposes the statement.
        "asserted-hypothesis",
    }
)
# Locations that build, render, or publish site content from data/trust.
PUBLISH_PATH_ROOTS = ("scripts", "src", "js", "_extensions", "_includes")
PUBLISH_PATH_FILES = ("_quarto.yml", "Makefile", "package.json")
GENERATED_TRUST_OUTPUTS = (
    "articles/_generated",
    "data/trust/generated",
    "reports",
)


def _drafts() -> dict[str, object]:
    data = json.loads(DRAFTS.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _registry() -> dict[str, object]:
    registry = _drafts()["registry"]
    assert isinstance(registry, dict)
    return registry


def _claims() -> list[tuple[dict[str, object], dict[str, object]]]:
    pages = _registry()["pages"]
    assert isinstance(pages, list)
    return [(page, claim) for page in pages for claim in page["claims"]]


def _records() -> dict[str, dict[str, object]]:
    records = _drafts()["review_records"]
    assert isinstance(records, list)
    by_id = {str(record["claim_id"]): record for record in records}
    assert len(by_id) == len(records), "duplicate review record"
    return by_id


def test_drafts_registry_is_schema_valid() -> None:
    validate_registry(_registry(), SCHEMA)


def test_at_least_twelve_drafts_cover_every_required_topic() -> None:
    claims = _claims()
    assert len(claims) >= 12
    topics = {str(record["topic"]) for record in _records().values()}
    assert REQUIRED_TOPICS <= topics, sorted(REQUIRED_TOPICS - topics)
    contraction = [r for r in _records().values() if r["topic"] == "tangent-space-contraction"]
    assert len(contraction) >= 2


def test_each_claim_has_exactly_one_pending_review_record() -> None:
    claim_ids = {str(claim["claim_id"]) for _, claim in _claims()}
    records = _records()
    assert set(records) == claim_ids
    for claim_id, record in records.items():
        signoff = record["owner_signoff"]
        assert isinstance(signoff, dict), claim_id
        assert signoff == {"status": "pending", "signed_off_by": None, "signed_off_on": None}


def test_no_draft_presents_itself_as_owner_approved() -> None:
    drafts = _drafts()
    assert drafts["publication_state"] == "unpublished-owner-review-draft"
    text = DRAFTS.read_text(encoding="utf-8").casefold()
    for phrase in ("owner-approved", "owner approved", '"status": "approved"', "signed off by"):
        assert phrase not in text, phrase
    for _, claim in _claims():
        # Critique review has not happened for a draft either.
        assert claim["critique_status"] == "not_reviewed", claim["claim_id"]


def test_evidence_rungs_use_the_ladder_and_disclose_their_basis() -> None:
    for claim_id, record in _records().items():
        basis = record["evidence_basis"]
        assert basis in EVIDENCE_BASES, claim_id
        rung = record["evidence_rung"]
        if basis == "asserted-hypothesis":
            assert rung is None, f"{claim_id}: an asserted hypothesis has reached no rung"
        else:
            assert rung in CANONICAL_RUNGS, claim_id
            # No draft may claim a rung that needs measured participant data.
            assert CANONICAL_RUNGS.index(str(rung)) <= CANONICAL_RUNGS.index(
                "qualified-simulation"
            ), claim_id
        assert str(record["evidence_note"]).strip(), claim_id


def test_hypothesis_claims_are_not_stated_above_hypothesis_strength() -> None:
    for page, claim in _claims():
        record = _records()[str(claim["claim_id"])]
        if record["evidence_basis"] == "asserted-hypothesis":
            assert claim["technical_claim"]["modal_strength"] == "hypothesis"
            assert claim["accessible_summary"]["modal_strength"] == "hypothesis"
        assert claim["technical_claim"]["modal_strength"] != "established", page["page_id"]


def test_every_source_page_and_heading_exists() -> None:
    for page, claim in _claims():
        record = _records()[str(claim["claim_id"])]
        source = ROOT / str(page["source_path"])
        assert source.is_file(), page["source_path"]
        assert record["source_page"] == page["source_path"]
        heading = str(record["source_heading"])
        text = source.read_text(encoding="utf-8")
        pattern = rf"^#{{2,4}} {re.escape(heading)}(?:\s*\{{[^}}]*\}})?\s*$"
        assert re.search(pattern, text, flags=re.MULTILINE), f"{claim['claim_id']}: {heading}"


def test_every_software_provenance_path_exists() -> None:
    for _, claim in _claims():
        for item in claim["software_provenance"]:
            assert item["repository"] == "D-sorganization/AffineDrift", claim["claim_id"]
            path = ROOT / str(item["path"])
            assert path.is_file(), f"{claim['claim_id']}: {item['path']}"


def test_drafts_are_not_in_the_published_registry() -> None:
    published = load_registry(REGISTRY, SCHEMA)
    published_ids = {
        str(claim["claim_id"]) for page in published["pages"] for claim in page["claims"]
    }
    draft_ids = {str(claim["claim_id"]) for _, claim in _claims()}
    assert not published_ids & draft_ids


def test_no_publish_path_reads_the_drafts_file() -> None:
    offenders: list[str] = []
    candidates = [ROOT / name for name in PUBLISH_PATH_FILES]
    for root in PUBLISH_PATH_ROOTS:
        candidates.extend(path for path in (ROOT / root).rglob("*") if path.is_file())
    for path in candidates:
        if not path.is_file() or path.suffix in {".pyc", ".png", ".svg", ".pdf", ".woff2"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if DRAFTS_NAME in text or "claim_registry_drafts" in text:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_no_generated_output_renders_a_draft_claim() -> None:
    draft_ids = [str(claim["claim_id"]) for _, claim in _claims()]
    for relative in GENERATED_TRUST_OUTPUTS:
        for path in (ROOT / relative).rglob("*"):
            if not path.is_file() or path.suffix not in {".qmd", ".json", ".md", ".html"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for claim_id in draft_ids:
                assert claim_id not in text, f"{claim_id} rendered in {path}"


def test_drafts_merge_into_a_schema_valid_registry_on_promotion() -> None:
    """Promotion after sign-off must not need a schema change for the records."""
    merged = copy.deepcopy(load_registry(REGISTRY, SCHEMA))
    by_source = {page["source_path"]: page for page in merged["pages"]}
    for page in copy.deepcopy(_registry()["pages"]):
        existing = by_source.get(page["source_path"])
        if existing is None:
            merged["pages"].append(page)
            by_source[page["source_path"]] = page
        else:
            existing["claims"].extend(page["claims"])
    validate_registry(merged, SCHEMA)


@pytest.mark.parametrize("field", ["falsifiers", "limitations", "valid_conditions"])
def test_each_draft_has_substantive_falsifiers_and_limits(field: str) -> None:
    for _, claim in _claims():
        values = claim[field]
        assert len(values) >= 2 or field == "valid_conditions", claim["claim_id"]
        assert all(len(str(value)) > 30 for value in values), claim["claim_id"]
        assert str(claim["next_validation_gate"]).strip()
