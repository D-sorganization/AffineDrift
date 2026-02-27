"""Quality checks for textbook readability and scientific traceability."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AFFINE_ARTICLE = REPO_ROOT / "articles" / "affine-nature-golf-swing.qmd"
BOOK_FILES = (
    REPO_ROOT / "books" / "tangent-space-methods.qmd",
    REPO_ROOT / "books" / "control-is-motion.qmd",
    REPO_ROOT / "books" / "biomechanics-biology-to-systems.qmd",
    REPO_ROOT / "books" / "human-motor-control.qmd",
)
FENCED_DIV_FILES = (
    AFFINE_ARTICLE,
    REPO_ROOT / "articles" / "The_Geometry_of_Motion" / "quarto" / "volume2_content.qmd",
)

REF_PATTERN = re.compile(r"@((?:sec|subsec|eq)-[A-Za-z0-9_:-]+)")
LABEL_PATTERN = re.compile(r"\{#([A-Za-z0-9_:-]+)\}")


def test_affine_article_internal_refs_are_resolved() -> None:
    """All local section/equation references should have matching labels."""
    text = AFFINE_ARTICLE.read_text(encoding="utf-8")
    refs = {match for match in REF_PATTERN.findall(text)}
    labels = {match for match in LABEL_PATTERN.findall(text)}
    missing = sorted(ref for ref in refs if ref not in labels)
    assert missing == []


def test_book_pages_include_scientific_status_and_traceability() -> None:
    """Volume pages should include scientific status and provenance context."""
    for book_file in BOOK_FILES:
        text = book_file.read_text(encoding="utf-8")
        assert "## Scientific Status" in text
        assert "## Source Traceability" in text


def test_book_pages_explain_notebooks_feature() -> None:
    """Volume pages should explain what notebooks are used for."""
    for book_file in BOOK_FILES:
        text = book_file.read_text(encoding="utf-8")
        assert "## Notebook Workflow" in text
        assert "notebooks/geometry_of_motion/" in text


def _collect_fenced_div_balance_issues(text: str) -> list[str]:
    """Return fenced-div balance issues outside fenced code blocks."""
    issues: list[str] = []
    depth = 0
    in_fenced_code = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_code = not in_fenced_code
            continue
        if in_fenced_code or not stripped.startswith(":::"):
            continue
        if stripped == ":::":
            depth -= 1
            if depth < 0:
                issues.append(f"line {line_no}: closing fenced div without opener")
                depth = 0
        else:
            depth += 1
    if depth != 0:
        issues.append(f"unclosed fenced div depth: {depth}")
    return issues


def test_target_pages_have_balanced_fenced_div_blocks() -> None:
    """Fenced div blocks should remain structurally balanced in target pages."""
    for qmd_file in FENCED_DIV_FILES:
        issues = _collect_fenced_div_balance_issues(qmd_file.read_text(encoding="utf-8"))
        assert issues == [], f"{qmd_file}: {issues}"
