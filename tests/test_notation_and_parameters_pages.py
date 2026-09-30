"""Parameters page and notation quick-reference card contract (issue #4551).

`PARAMETERS.md` was previously rendered nowhere, and `pages/notation.qmd`
duplicated its included heading and a manual table of contents. These tests
pin the fix: a rendered parameters page, a one-page notation quick-reference
card, and NOTATION.md/PARAMETERS.md free of the duplicated boilerplate.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _front_matter(path: Path) -> dict[str, object]:
    """Parse the YAML front matter block of a qmd file (test-only helper)."""
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} is missing YAML front matter"
    end = text.index("\n---", 4)
    return yaml.safe_load(text[4:end]) or {}


def test_parameters_page_renders_parameters_md() -> None:
    page = REPO_ROOT / "pages" / "parameters.qmd"
    assert page.is_file(), "pages/parameters.qmd must exist to render PARAMETERS.md"
    text = page.read_text(encoding="utf-8")
    assert "{{< include ../PARAMETERS.md >}}" in text
    assert _front_matter(page).get("categories") == ["reference"]


def test_notation_quick_reference_card_exists() -> None:
    page = REPO_ROOT / "pages" / "notation-quick-reference.qmd"
    assert page.is_file(), "a one-page printable notation quick-reference card must exist"
    assert _front_matter(page).get("categories") == ["reference"]


def test_notation_md_has_no_duplicate_heading_or_toc() -> None:
    text = (REPO_ROOT / "NOTATION.md").read_text(encoding="utf-8")
    assert "## Mathematical Notation Reference" not in text
    assert "## Table of Contents" not in text


def test_parameters_md_has_no_duplicate_heading() -> None:
    text = (REPO_ROOT / "PARAMETERS.md").read_text(encoding="utf-8")
    assert "# Canonical Parameters Reference" not in text
