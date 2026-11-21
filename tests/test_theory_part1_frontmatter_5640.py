"""Theory Part 1 YAML front matter contracts (#5640, Gemini CVE-A1)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
THEORY = ROOT / "articles" / "theory-part1.qmd"


def _front_matter_block() -> str:
    text = THEORY.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    return text[4:end]


@pytest.mark.content_lint
def test_theory_part1_front_matter_matches_control_affine_contract() -> None:
    """Front matter must not equate control with muscle force or overclaim a strict split."""
    fm = _front_matter_block().lower()
    for phrase in (
        "active muscle force",
        "natural drift and active muscle",
        "strict control-affine decomposition into drift and input",
        "encapsulates all passive gravitational",
        "date unverified",
    ):
        assert phrase not in fm, f"stale takeaway still present: {phrase}"
    assert "generalized torque" in fm
    assert "not biological muscle" in fm or "not individual muscle" in fm
    assert "omitted" in fm or "aerodynamic drag" in fm


@pytest.mark.content_lint
def test_theory_part1_has_reviewed_publication_date() -> None:
    fm = _front_matter_block()
    assert 'date: "Date unverified"' not in fm
    assert "date:" in fm
    assert "date-modified:" in fm or "last-reviewed:" in fm
