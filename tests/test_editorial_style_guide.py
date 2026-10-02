"""test_editorial_style_guide.py

Tests for [WEB-12.1] (#4587) Write the Editorial Style Guide.
Validates existence, structure, acceptance criteria, cross-references,
and scanner contracts for editorial prose standards.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITORIAL_GUIDE = ROOT / "docs" / "development" / "editorial-style-guide.md"
CONTRIBUTING_MD = ROOT / "CONTRIBUTING.md"
NEW_ARTICLE_TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "new-article-proposal.md"

REQUIRED_SECTIONS = [
    "Voice and Tone",
    "Scope and Mathematical Confidence",
    "Where Caveats Go",
    "Glossary Linking",
    "Readability Targets",
    "Analogy and Metaphor Rules",
    "Banned Internal Vocabulary",
    "Capitalization and Headings",
]

BANNED_INTERNAL_TERMS = [
    "readiness-program",
    "claim-audit",
    "ztcf-gate",
    "phantom-merge",
    "weak-assertion",
    "tier:strong",
    "tier:cli",
]


def test_editorial_style_guide_exists_and_covers_required_sections() -> None:
    """Ensure docs/development/editorial-style-guide.md exists and contains all required sections."""
    assert EDITORIAL_GUIDE.exists(), f"Editorial style guide missing at {EDITORIAL_GUIDE}"
    content = EDITORIAL_GUIDE.read_text(encoding="utf-8")
    assert (
        len(content.splitlines()) >= 150
    ), "Editorial style guide must be comprehensive (>= 150 lines)"

    for section in REQUIRED_SECTIONS:
        assert section.lower() in content.lower(), f"Missing required section: '{section}'"


def test_editorial_guide_defines_voice_and_caveat_standards() -> None:
    """Verify normative standards for mathematical confidence and WEB-03.4 caveat placement."""
    content = EDITORIAL_GUIDE.read_text(encoding="utf-8")

    # Confident mathematics, explicit scope
    assert "mathematics" in content.lower()
    assert "scope" in content.lower()
    assert "assumption" in content.lower()

    # WEB-03.4 block reference
    assert "what this shows" in content.lower()
    assert "what it does not show" in content.lower()


def test_editorial_guide_specifies_glossary_and_readability_targets() -> None:
    """Verify glossary shortcode requirements and per-layer readability metrics."""
    content = EDITORIAL_GUIDE.read_text(encoding="utf-8")

    # Glossary shortcode
    assert "{{< term" in content or "shortcode" in content.lower()

    # Readability: lay block <= grade 10; body unconstrained
    assert "grade 10" in content.lower() or "flesch-kincaid" in content.lower()
    assert "unconstrained" in content.lower() or "body" in content.lower()

    # Analogy boundary rule: "say where the analogy breaks"
    assert "break" in content.lower() and "analogy" in content.lower()


def test_editorial_guide_defines_banned_vocabulary_list() -> None:
    """Verify that internal process/engineering jargon is explicitly listed as prohibited in reader prose."""
    content = EDITORIAL_GUIDE.read_text(encoding="utf-8")
    for term in BANNED_INTERNAL_TERMS:
        assert term in content, f"Banned vocabulary list must document prohibition of '{term}'"


def test_contributing_and_issue_template_reference_editorial_guide() -> None:
    """Ensure CONTRIBUTING.md and new-article template reference the editorial style guide."""
    assert CONTRIBUTING_MD.exists()
    contrib_text = CONTRIBUTING_MD.read_text(encoding="utf-8")
    assert (
        "editorial-style-guide" in contrib_text or "Editorial Style Guide" in contrib_text
    ), "CONTRIBUTING.md must link to docs/development/editorial-style-guide.md"

    assert NEW_ARTICLE_TEMPLATE.exists()
    template_text = NEW_ARTICLE_TEMPLATE.read_text(encoding="utf-8")
    assert (
        "editorial-style-guide" in template_text or "Editorial Style Guide" in template_text
    ), "new-article-proposal.md must reference the Editorial Style Guide"
