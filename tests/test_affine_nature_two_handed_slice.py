"""Slice-1 contract for the dual-register two-handed account.

The flagship article may state the panel wrench family in prose. It may not
invent swing figures, attach a replay badge to a number, or finish the
flagship while no admitted two-handed export is wired in.
"""

from __future__ import annotations

from pathlib import Path

ARTICLE = Path(__file__).resolve().parents[1] / "articles/affine-nature-golf-swing.qmd"
SLICE_START = "## Two-Handed Null Space in Two Registers"
SLICE_END = "## Evidence Needed for a Golf Interpretation"
FORBIDDEN = ("wasted energy", "biologically optimal")


def _article_text() -> str:
    """Return the flagship article source."""
    return ARTICLE.read_text(encoding="utf-8")


def _slice_text() -> str:
    """Return the dual-register section, excluding the following section."""
    text = _article_text()
    start = text.index(SLICE_START)
    end = text.index(SLICE_END, start)
    return text[start:end]


def test_slice_callout_states_that_exports_are_pending() -> None:
    """The pending-export callout is visible and denies flagship completion."""
    section = _slice_text()
    assert "Figures and results in this section are pending verified simulation exports." in section
    assert "No admitted two-handed simulation export is wired in." in section
    assert "This slice does not complete the flagship." in section
    assert section.count("Schematic Placeholder:") == 3
    assert "![" not in section


def test_layman_register_uses_the_declared_story() -> None:
    """ZTCF, ZVCF, and the least-force hand split use the layman wording."""
    section = _slice_text()
    assert "ZTCF is the club's natural drift." in section
    assert "ZVCF is the golfer's active effort." in section
    assert "without the hands fighting each other." in section
    assert "minimum-squared-force" in section


def test_scientist_register_states_the_panel_oracle() -> None:
    """The wrench family, invariants, objectives, and couple policy are present."""
    section = _slice_text()
    assert r"M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau." in section
    assert r"f_L&=F/2+(u\times m')/d+\alpha u" in section
    assert r"f_R&=F/2-(u\times m')/d-\alpha u" in section
    assert r"u\cdot m'=0." in section
    assert r"\mathrm{ZVCF}=\mathrm{Total}-\mathrm{ZTCF}" in section
    assert "axial-only" in section
    assert "bounded variant" in section
    assert "$J_F$" in section
    assert r"C=\lVert f_L\rVert+\lVert f_R\rVert-\lVert F\rVert." in section
    assert "`allocation-only`" in section
    assert "`forward-replayed`" in section


def test_article_keeps_one_lay_block_and_avoids_forbidden_claims() -> None:
    """The shared lay block stays singular, and the forbidden phrases stay out."""
    text = _article_text().lower()
    assert text.count("::: {.laymans-terms}") == 1
    for phrase in FORBIDDEN:
        assert phrase not in text
