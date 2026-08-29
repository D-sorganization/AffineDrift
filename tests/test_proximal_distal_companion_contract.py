"""Publication contracts for the accessible proximal-distal companion."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"
FIGURES = ROOT / "articles/figures/proximal_distal_companion"
PDF_SOURCE = ROOT / "articles/proximal-distal-a-journey-through-the-swing.pdf"
PDF_OUTPUT = ROOT / "docs/articles/proximal-distal-a-journey-through-the-swing.pdf"
WORKBENCH = ROOT / "articles/proximal-distal-model-workbench.qmd"
CHAPTERS = ROOT / "articles/proximal_distal_companion/chapters"
# UpstreamDrift main artifact at merge b6a64e174423870f341991a7b8ba9465c84209b9.
# This records the reviewed publication rather than the obsolete first-pass floor.
TECHNICAL_MONOGRAPH_PAGE_COUNT = 181
TECHNICAL_MONOGRAPH_EXTRACTED_WORD_COUNT = 69_257


def _source() -> str:
    return ARTICLE.read_text(encoding="utf-8")


def _chapter_source() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(CHAPTERS.glob("ch??_*.qmd"))
    )


def _book_source() -> str:
    """Resolve the manuscript's Quarto includes for source-level contracts."""
    return f"{_source()}\n{_chapter_source()}"


def test_companion_pdf_has_a_stable_source_and_publication_path() -> None:
    config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert PDF_SOURCE.is_file() and PDF_SOURCE.stat().st_size > 100_000
    assert PDF_OUTPUT.is_file() and PDF_OUTPUT.read_bytes() == PDF_SOURCE.read_bytes()
    assert "- articles/proximal-distal-a-journey-through-the-swing.pdf" in config
    assert "- docs/articles/proximal-distal-a-journey-through-the-swing.pdf" not in config
    assert "pypdf==6.16.1" in requirements


def test_companion_has_complete_book_like_reader_architecture() -> None:
    source = _book_source()
    required_sections = (
        "# Follow the Energy",
        "# Choose the System Before Counting",
        "# Speed, Acceleration, Energy, and Power",
        "# Constraints Push Back",
        "# Two Hands Make One Visible Wrench",
        "# Negative Torque Can Help a Positive Outcome",
        "# The Shaft Is a Spring With a Memory",
        "# Timing Is a State Question, Not Just a Clock Question",
        "# Fast Once Is Not the Same as Robustly Fast",
        "# Sensitivity and Identifiability",
        "# A Ladder of Models, Not One Final Model",
        "# Design an Experiment That Can Say No",
        "# A Practical Synthesis Without a Swing Prescription",
        "# Walk Through a Whole Swing Without Losing the Ledger",
        "# A Curious Golfer and a Skeptical Reviewer Ask the Hard Questions",
        "# Glossary",
        "# References",
    )
    for heading in required_sections:
        assert heading in source


def test_metaphors_are_bounded_and_scientific_claim_classes_are_explicit() -> None:
    source = _book_source().casefold()
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
    source = _book_source()
    images = re.findall(r"!\[([^\]]+)\]\((figures/proximal_distal_companion/[^)]+)\)", source)
    assert len(images) >= 12
    assert len({path for _, path in images}) >= 12
    assert all(len(alt.strip()) >= 30 for alt, _ in images)


def test_every_companion_figure_has_svg_and_pdf_variants() -> None:
    source = _book_source()
    stems = {
        Path(path).stem
        for path in re.findall(r"figures/proximal_distal_companion/([^)]+\.svg)", source)
    }
    assert len(stems) >= 12
    for stem in stems:
        for suffix in ("svg", "pdf"):
            path = FIGURES / f"{stem}.{suffix}"
            assert path.is_file() and path.stat().st_size > 1_000


def test_companion_figure_generator_uses_stable_svg_identifiers() -> None:
    generator = (ROOT / "scripts/make_proximal_distal_companion_figures.py").read_text(
        encoding="utf-8"
    )
    assert '"svg.hashsalt": "proximal-distal-companion-v1"' in generator


def test_reader_can_reach_evidence_technical_treatment_and_primary_sources() -> None:
    source = _book_source()
    assert "proximal_distal_energy_transfer.pdf" in source
    assert "transmission_robustness_study.json" in source
    assert source.count("Go Deeper") >= 8
    citation_keys = set(re.findall(r"@([A-Za-z][A-Za-z0-9:_-]+)", source))
    bibliography = (ROOT / "references/proximal-distal-energy.bib").read_text(encoding="utf-8")
    declared = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bibliography))
    assert citation_keys <= declared
    assert len(citation_keys) >= 12


def test_article_never_mentions_prompt_or_style_exemplar() -> None:
    source = _book_source().casefold()
    forbidden = ("thesis length", "user requested", "prompt", "feynman")
    assert not any(term in source for term in forbidden)


def test_model_workbench_page_is_discoverable_and_uses_canonical_tools() -> None:
    """The reader page must link to one shared simulator, not copy its glossary."""
    article_index = (ROOT / "resources/articles.qmd").read_text(encoding="utf-8")
    article = _source()
    workbench = WORKBENCH.read_text(encoding="utf-8")

    assert "articles/proximal-distal-model-workbench.html" in article_index
    assert "proximal-distal-model-workbench.html" in article
    assert "D-sorganization/Tools/tree/main/src/pendulum_simulator" in workbench
    assert "companion_catalog.json" in workbench
    assert "PyQt6" in workbench and "React/Tauri" in workbench
    assert "exploratory_model_output" in workbench
    for heading in (
        "# Explore the Models",
        "## Choose a Guided Experiment",
        "## What Would Count Against the Mechanism?",
        "## Run It Locally",
        "## Interpretation Boundary",
    ):
        assert heading in workbench


def test_included_chapter_workbench_links_are_valid_when_rendered_independently() -> None:
    """Quarto also renders include fragments at their own nested public URLs."""
    for chapter_name in ("ch03_state_snapshot.qmd", "ch28_practical_synthesis.qmd"):
        chapter = (CHAPTERS / chapter_name).read_text(encoding="utf-8")
        assert "](/articles/proximal-distal-model-workbench.html)" in chapter
        assert "](proximal-distal-model-workbench.html)" not in chapter


def test_expanded_companion_has_one_substantive_file_per_registered_chapter() -> None:
    """The lay book is a developed manuscript, not a collection of short cards."""
    chapter_paths = sorted(CHAPTERS.glob("ch??_*.qmd"))
    assert len(chapter_paths) == 30

    for expected_number, chapter_path in enumerate(chapter_paths, start=1):
        chapter = chapter_path.read_text(encoding="utf-8")
        words = re.findall(r"\b[\w'-]+\b", chapter)
        assert chapter.startswith("## ")
        assert f"{{#sec-lay-ch{expected_number:02d}" in chapter
        assert len(words) >= 2_000, f"{chapter_path.name} has only {len(words)} words"
        assert "## A Concrete Picture" in chapter
        assert "## How the Mechanism Works" in chapter
        assert "## Where the Picture Breaks" in chapter
        assert "**Go Deeper:**" in chapter


def test_expanded_companion_meets_visual_reference_and_navigation_density() -> None:
    combined = _book_source()
    figure_paths = set(re.findall(r"figures/proximal_distal_companion/([^)]+\.svg)", combined))
    live_links = re.findall(r"https://[^)\s]+", combined)
    citation_keys = set(re.findall(r"@([A-Za-z][A-Za-z0-9:_-]+)", combined))

    assert len(figure_paths) >= 30
    assert len(live_links) >= 25
    assert len(citation_keys) >= 20
    assert combined.count("**Model Result:**") >= 10
    assert combined.count("**Human Evidence:**") >= 5
    assert combined.count("**Hypothesis:**") >= 5
    assert combined.count("**Practical Interpretation:**") >= 5


def test_expanded_companion_pdf_is_at_least_as_long_as_the_technical_monograph() -> None:
    reader = PdfReader(PDF_SOURCE)
    assert len(reader.pages) >= TECHNICAL_MONOGRAPH_PAGE_COUNT
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # Use the same whitespace-token extraction recorded for the comparison PDF.
    # A regex tokenizer produces a different count for equations and punctuation.
    extracted_words = extracted_text.split()
    assert len(extracted_words) >= TECHNICAL_MONOGRAPH_EXTRACTED_WORD_COUNT
    assert len(reader.outline) >= 50
    uri_count = sum(
        1
        for page in reader.pages
        for annotation in (page.get("/Annots") or [])
        if annotation.get_object().get("/A", {}).get("/URI")
    )
    assert uri_count >= 60


def test_workbench_exposes_drift_transfer_diagnostics() -> None:
    text = WORKBENCH.read_text(encoding="utf-8")

    assert "Drift Transfer" in text
    assert "Negative Grip Work" in text
    assert "proximal-link angular velocity" in text


def test_companion_explains_coordinate_force_sources_without_double_counting() -> None:
    source = _book_source()

    for phrase in (
        "Coriolis Cross Term",
        "Squared-Speed Term",
        "coordinate-dependent",
        "not forces to add",
        "13.817 N s",
        "rank-deficient",
    ):
        assert phrase in source


def test_workbench_exposes_coordinate_force_source_diagnostics() -> None:
    text = WORKBENCH.read_text(encoding="utf-8")

    assert "Full-Trajectory Coordinate Force Sources" in text
    assert "signed and absolute tangent impulse" in text
    assert "force-attribution/v1" in text
