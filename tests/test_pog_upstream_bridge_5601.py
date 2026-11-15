"""PoG ZTCF and constraint chapters: UpstreamDrift bridge contracts (#5601)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/companion/upstream_implementation_links.json"
CH06 = ROOT / "articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd"
CH07 = ROOT / "articles/The_Physics_of_Golf/quarto/ch07_constraint_forces.qmd"


def test_ch06_and_ch07_listed_in_upstream_implementation_ledger() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ids = {entry["id"] for entry in ledger["bridges"]}
    assert "pog-ch06-ztcf" in ids
    assert "pog-ch07-constraints" in ids


def test_ch06_links_rendered_notation_and_includes_upstream_bridge() -> None:
    text = CH06.read_text(encoding="utf-8")
    assert "NOTATION.md" not in text
    assert "pages/notation.html" in text
    assert "upstream-implementation/pog-ch06" in text


def test_ch07_includes_upstream_bridge_and_names_rnea_cross_check_test() -> None:
    text = CH07.read_text(encoding="utf-8")
    assert "upstream-implementation/pog-ch07" in text
    assert "test_constraint_forces_rigor" in text
