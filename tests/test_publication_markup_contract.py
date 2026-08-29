"""Structural markup contracts for Quarto publication sources."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


PUBLICATION_SOURCES = (
    REPO_ROOT / "articles" / "controllability-drift-ratio.qmd",
    REPO_ROOT
    / "articles"
    / "The_Physics_of_Golf"
    / "quarto"
    / "ch18_inverse_dynamics_parallel.qmd",
)


def test_fenced_divs_are_balanced_in_standalone_publication_sources() -> None:
    """An unclosed fenced Div can silently swallow the remainder of a page."""
    offenders: list[str] = []
    for source in PUBLICATION_SOURCES:
        text = source.read_text(encoding="utf-8")
        openings = len(re.findall(r"^:::[ \t]+\S", text, flags=re.MULTILINE))
        closings = len(re.findall(r"^:::[ \t]*$", text, flags=re.MULTILINE))
        if openings != closings:
            offenders.append(f"{source.relative_to(REPO_ROOT)}: {openings} open, {closings} closed")

    assert offenders == [], "Unbalanced fenced Divs:\n" + "\n".join(offenders)


def test_physics_textbook_uses_explicit_links_for_cross_document_sections() -> None:
    """Website pages cannot resolve Quarto section references owned by another page."""
    chapter_dir = REPO_ROOT / "articles" / "The_Physics_of_Golf" / "quarto"
    sources = sorted(chapter_dir.glob("*.qmd"))
    owners: dict[str, Path] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for label in re.findall(r"\{#(sec-[A-Za-z0-9_-]+)\}", text):
            owners[label] = source

    offenders: list[str] = []
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label in re.findall(r"(?<![A-Za-z0-9_])@(sec-[A-Za-z0-9_-]+)", line):
                owner = owners.get(label)
                if owner is not None and owner != source:
                    offenders.append(
                        f"{source.name}:{line_number} references {label} owned by {owner.name}"
                    )

    assert offenders == [], "Cross-document @sec references must be links:\n" + "\n".join(offenders)
