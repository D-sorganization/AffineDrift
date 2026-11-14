"""Contract tests for onboarding copy, ladder/badge consistency, and count sync (#5594)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.generate_content_inventory import main, render_accessibility_with_page_count

ROOT = Path(__file__).resolve().parents[1]
STATES = "Available Validated Experimental Planned Deprecated Opinion".split()
BANNED = (
    "active muscular control|muscular torque|golfer effort|golfer's muscles add|"
    "active golfer control push|golfer-injected control|muscles stopped pushing"
).split("|")
F12_FILES = (
    "index.qmd pages/start-here.qmd pages/scope-and-limits.qmd pages/validation-roadmap.qmd "
    "data/trust/claim_registry.json _includes/generated/claims-ledger.qmd "
    "articles/_generated/trust/ad-ztcf-attribution.qmd"
).split()


def _r(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_f12_declared_control_and_drift_wording() -> None:
    for rel in F12_FILES:
        assert all(p not in _r(rel).lower() for p in BANNED), rel
    sh = _r("pages/start-here.qmd").lower()
    assert all(k in sh for k in ("passive loads", "constraint", "declared input"))
    assert (
        "dimensional consistency, coordinate invariance"
        not in _r("pages/scope-and-limits.qmd").lower()
    )


def test_f17_single_ladder_and_f21_counts_and_notation_date() -> None:
    rm = _r("pages/validation-roadmap.qmd")
    assert "four-rung" not in rm.lower() and "terminal rung of the validation ladder" not in rm
    assert all(f"### Rung {n}:" not in rm for n in (1, 2, 3))
    assert all(f"Stage {c}" in rm for c in "ABCD")
    for rel in ("pages/how-to-read.qmd", "pages/tools.qmd", "index.qmd"):
        assert all(s in _r(rel) for s in STATES), rel
    idx = _r("index.qmd")
    assert "Working Draft" not in idx and "Outline Only" not in idx
    htr = _r("pages/how-to-read.qmd")
    assert "Control-Affine Foundations" in htr and "Numerical Consistency" in htr
    assert (
        "Theory Part 1: Control-Affine Derivation" not in htr
        and "Numerical Verification Protocol" not in htr
    )
    count = int(json.loads(_r("data/content/inventory.json"))["page_count"])
    assert f"{count} pages" in _r("pages/content-inventory.qmd")
    m = re.search(r"page-count-start -->(\d+)<!--", _r("pages/accessibility.qmd"))
    assert (
        m is not None
        and int(m.group(1)) == count
        and "**Last Updated:** April 2026" not in _r("NOTATION.md")
    )
    sample = "<!-- content-inventory:page-count-start -->1<!-- content-inventory:page-count-end -->"
    assert ">254<!--" in render_accessibility_with_page_count(sample, 254)
    assert main(["--sync-accessibility-from-json", "--check"]) == 0
