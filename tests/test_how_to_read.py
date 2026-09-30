"""Tests for the 'How to Read This Site' guide and canonical publication states (WEB-01.6 / #4491).

Enforces:
1. pages/how-to-read.qmd exists with valid metadata (70-160 char description).
2. It serves as the single source of truth for the six publication states (#publication-states).
3. Redundant inline definitions in index.qmd and pages/development-roadmap.qmd are removed/consolidated.
4. Badge and status pill components link to how-to-read.html#publication-states.
5. All internal links in pages/how-to-read.qmd resolve.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOW_TO_READ_PATH = ROOT / "pages" / "how-to-read.qmd"

CANONICAL_STATES = {
    "Available",
    "Validated",
    "Experimental",
    "Planned",
    "Deprecated",
    "Opinion",
}


def test_how_to_read_page_metadata() -> None:
    """Verify page exists, has title and 70-160 char description."""
    assert HOW_TO_READ_PATH.is_file(), f"Missing {HOW_TO_READ_PATH}"
    content = HOW_TO_READ_PATH.read_text(encoding="utf-8")
    assert content.startswith("---")
    parts = content.split("---", 2)
    assert len(parts) >= 3
    fm = parts[1]

    desc_match = re.search(r'^description:\s*["\']?([^"\']+)["\']?$', fm, re.MULTILINE)
    assert desc_match is not None, "description missing from frontmatter"
    desc = desc_match.group(1).strip()
    assert 70 <= len(desc) <= 160, f"Description length {len(desc)} not in 70-160 range: '{desc}'"

    title_match = re.search(r'^title:\s*["\']?([^"\']+)["\']?$', fm, re.MULTILINE)
    assert title_match is not None, "title missing from frontmatter"


def test_single_source_of_publication_states() -> None:
    """Verify pages/how-to-read.qmd defines all 6 canonical states under #publication-states."""
    content = HOW_TO_READ_PATH.read_text(encoding="utf-8")
    assert "{#publication-states}" in content

    for state in CANONICAL_STATES:
        assert f"**{state}**" in content, f"State '{state}' missing from canonical table"


def test_index_and_roadmap_consolidated_to_guide() -> None:
    """Verify index.qmd and pages/development-roadmap.qmd link to how-to-read guide without duplicate tables."""
    index_content = (ROOT / "index.qmd").read_text(encoding="utf-8")
    assert "pages/how-to-read.html" in index_content or "how-to-read.html" in index_content
    # Inline 6-state definitions must be removed
    assert "Available means a page or program can be opened;" not in index_content

    roadmap_content = (ROOT / "pages" / "development-roadmap.qmd").read_text(encoding="utf-8")
    assert "how-to-read.html#publication-states" in roadmap_content
    # The duplicate Markdown table should not be present in roadmap
    assert "| **Validated** | A specific claim names its validation evidence" not in roadmap_content


def test_tools_status_pills_link_to_guide() -> None:
    """Verify status badge components in pages/tools.qmd link to publication states."""
    tools_content = (ROOT / "pages" / "tools.qmd").read_text(encoding="utf-8")
    assert (
        '<a href="how-to-read.html#publication-states" class="status-badge' in tools_content
        or '<a href="how-to-read.html#publication-states" class="status-pill' in tools_content
    )
    # Non-canonical EXPLORATORY label should be gone
    assert "EXPLORATORY" not in tools_content


def test_quarto_navigation_includes_how_to_read() -> None:
    """Verify _quarto.yml includes How to Read This Site in navigation/footer."""
    quarto_content = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    assert "pages/how-to-read.html" in quarto_content


def test_how_to_read_internal_links_resolve() -> None:
    """Verify all relative markdown links in pages/how-to-read.qmd point to existing files."""
    content = HOW_TO_READ_PATH.read_text(encoding="utf-8")
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for _text, target in link_pattern.findall(content):
        if target.startswith(("http", "#", "mailto:")):
            continue
        clean_target = target.split("#")[0].split("?")[0]
        if not clean_target:
            continue
        resolved = (HOW_TO_READ_PATH.parent / clean_target).resolve()
        if resolved.suffix == ".html":
            qmd_candidate = resolved.with_suffix(".qmd")
            md_candidate = resolved.with_suffix(".md")
            index_candidate = resolved.parent / resolved.stem / "index.qmd"
            exists = (
                resolved.is_file()
                or qmd_candidate.is_file()
                or md_candidate.is_file()
                or index_candidate.is_file()
            )
            assert exists, f"Broken link in how-to-read.qmd: '{target}' -> {resolved}"
        else:
            assert resolved.exists(), f"Broken link in how-to-read.qmd: '{target}' -> {resolved}"
