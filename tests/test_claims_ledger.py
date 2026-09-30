"""Contracts for the reader-facing Claim Ledger page (evidence/claims.qmd)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_claims_ledger import (
    PAGE_LINKS_DIR,
    PARTIAL,
    ClaimLedgerError,
    build_claim_cards,
    generate,
    render_ledger_partial,
)

ROOT = Path(__file__).resolve().parents[1]
CLAIMS_PAGE = ROOT / "evidence/claims.qmd"
DCR_PAGE = ROOT / "articles/drift-control-ratio.qmd"


def _dcr_card() -> dict[str, object]:
    cards = build_claim_cards(ROOT)
    matches = [card for card in cards if card["claim_id"] == "ad-dcr-001"]
    assert len(matches) == 1
    return matches[0]


def test_build_claim_cards_projects_the_governed_claim() -> None:
    card = _dcr_card()

    assert card["title"] == "DCR Is Not a Reachability Certificate"
    assert card["anchor"] == "claim-ad-dcr-001"
    assert "acceleration imbalance" in str(card["plain_statement"])
    assert "reachability" in str(card["formal_statement"]).lower()
    assert "Mathematical Identity" in str(card["rung_label"])


def test_build_claim_cards_carries_the_full_falsifier_list() -> None:
    card = _dcr_card()
    falsifiers = card["falsifiers"]
    assert isinstance(falsifiers, list)
    assert len(falsifiers) == 2
    assert any("reachable-interval width" in item for item in falsifiers)
    assert any("uniquely determines a finite-horizon" in item for item in falsifiers)


def test_build_claim_cards_links_related_critiques() -> None:
    card = _dcr_card()
    critiques = card["critiques"]
    assert isinstance(critiques, list)
    critique_ids = {item["critique_id"] for item in critiques}
    assert critique_ids == {
        "crit-dimensional-inconsistency-dcr",
        "crit-lie-bracket-formalism-overreach",
        "crit-normative-ambiguity-drift",
        "crit-planar-dcr-blindness",
        "crit-precision-gross-control",
    }
    for item in critiques:
        assert item["title"]
        assert item["status"] in {"open", "responded", "adjudicated", "resolved", "rejected"}
        assert item["route"]


def test_build_claim_cards_lists_the_pages_that_make_the_claim() -> None:
    card = _dcr_card()
    assert card["pages"] == ["articles/drift-control-ratio.qmd"]


def test_render_ledger_partial_is_keyboard_and_screen_reader_accessible() -> None:
    cards = build_claim_cards(ROOT)
    partial = render_ledger_partial(cards, digest="0" * 64)

    assert 'role="region"' in partial
    assert "aria-label=" in partial
    assert "{#claim-ad-dcr-001}" in partial
    assert "DO NOT EDIT" in partial
    assert "reachable-interval width" in partial
    assert "crit-dimensional-inconsistency-dcr" in partial
    assert "Drift, Control Capacity and Golf-Swing Correction" in partial


def test_generate_produces_current_and_deterministic_artifacts() -> None:
    first = generate(check=False, root=ROOT)
    second = generate(check=True, root=ROOT)

    assert first == second
    assert PARTIAL in first
    for path in first:
        assert path.is_file()


def test_generate_writes_a_link_partial_for_every_page_that_makes_a_claim() -> None:
    generate(check=False, root=ROOT)
    link_partial = PAGE_LINKS_DIR / "drift-control-ratio.qmd"
    assert link_partial.is_file()
    content = link_partial.read_text(encoding="utf-8")
    assert "evidence/claims.html#claim-ad-dcr-001" in content


def test_dcr_page_includes_its_generated_claim_ledger_link() -> None:
    source = DCR_PAGE.read_text(encoding="utf-8")
    assert "{{< include ../_includes/generated/claims-ledger/drift-control-ratio.qmd >}}" in source


def test_claims_page_includes_the_generated_ledger_partial() -> None:
    source = CLAIMS_PAGE.read_text(encoding="utf-8")
    assert "{{< include ../_includes/generated/claims-ledger.qmd >}}" in source
    assert "categories:" in source


def test_write_or_check_detects_staleness(tmp_path: Path) -> None:
    from scripts.generate_claims_ledger import _write_or_check

    target = tmp_path / "out.qmd"
    _write_or_check(target, "first\n", check=False)

    with pytest.raises(ClaimLedgerError):
        _write_or_check(target, "second\n", check=True)

    _write_or_check(target, "second\n", check=False)
    _write_or_check(target, "second\n", check=True)
