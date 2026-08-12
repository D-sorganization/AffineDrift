"""Publication contracts for the accessible proximal-distal companion."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"
FIGURES = ROOT / "articles/figures/proximal_distal_companion"
PDF_SOURCE = ROOT / "articles/proximal-distal-a-journey-through-the-swing.pdf"
PDF_OUTPUT = ROOT / "docs/articles/proximal-distal-a-journey-through-the-swing.pdf"


def _source() -> str:
    return ARTICLE.read_text(encoding="utf-8")


def test_companion_pdf_has_a_stable_source_and_publication_path() -> None:
    config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    assert PDF_SOURCE.is_file() and PDF_SOURCE.stat().st_size > 100_000
    assert PDF_OUTPUT.is_file() and PDF_OUTPUT.read_bytes() == PDF_SOURCE.read_bytes()
    assert "- articles/proximal-distal-a-journey-through-the-swing.pdf" in config
    assert "- docs/articles/proximal-distal-a-journey-through-the-swing.pdf" not in config


def test_companion_has_complete_book_like_reader_architecture() -> None:
    source = _source()
    required_sections = (
        "# Prologue: Follow the Energy",
        "# A Swing Is a Moving System",
        "# Speed Is Not Energy",
        "# The Club Is Carried Before It Is Released",
        "# Forces Travel Through Connections",
        "# Two Hands Can Make a Turning Effect",
        "# Negative Torque Is Not a Negative Intention",
        "# A Shaft Can Store and Return Energy",
        "# Timing by the Clock and Timing by the State",
        "# Fast Once or Fast Repeatedly",
        "# Many Motions Can Share One Outcome",
        "# What the Models Can and Cannot Tell Us",
        "# A Research Program That Can Be Wrong",
        "# Glossary",
        "# References",
    )
    for heading in required_sections:
        assert heading in source


def test_metaphors_are_bounded_and_scientific_claim_classes_are_explicit() -> None:
    source = _source().casefold()
    assert source.count("where the picture breaks") >= 8
    for phrase in (
        "model result",
        "human evidence",
        "hypothesis",
        "not a coaching instruction",
        "would count against",
        "pointwise",
        "forward counterfactual",
    ):
        assert phrase in source


def test_companion_has_substantive_visual_density_and_alt_text() -> None:
    source = _source()
    images = re.findall(r"!\[([^\]]+)\]\((figures/proximal_distal_companion/[^)]+)\)", source)
    assert len(images) >= 12
    assert len({path for _, path in images}) >= 12
    assert all(len(alt.strip()) >= 30 for alt, _ in images)


def test_every_companion_figure_has_svg_and_pdf_variants() -> None:
    source = _source()
    stems = {
        Path(path).stem
        for path in re.findall(r"figures/proximal_distal_companion/([^)]+\.svg)", source)
    }
    assert len(stems) >= 12
    for stem in stems:
        for suffix in ("svg", "pdf"):
            path = FIGURES / f"{stem}.{suffix}"
            assert path.is_file() and path.stat().st_size > 1_000


def test_reader_can_reach_evidence_technical_treatment_and_primary_sources() -> None:
    source = _source()
    assert "proximal_distal_energy_transfer.pdf" in source
    assert "transmission_robustness_study.json" in source
    assert source.count("Go Deeper") >= 8
    citation_keys = set(re.findall(r"@([A-Za-z][A-Za-z0-9:_-]+)", source))
    bibliography = (ROOT / "references/proximal-distal-energy.bib").read_text(encoding="utf-8")
    declared = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bibliography))
    assert citation_keys <= declared
    assert len(citation_keys) >= 12


def test_article_never_mentions_prompt_or_style_exemplar() -> None:
    source = _source().casefold()
    forbidden = ("thesis length", "user requested", "prompt", "feynman")
    assert not any(term in source for term in forbidden)
