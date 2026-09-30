"""Tests for website page titles and meta descriptions (WEB-10.7, #4575).

Enforces that:
1. The home page title is descriptive (not generic "Home").
2. Every published page in sitemap.xml has a non-empty and globally unique title.
3. Every published page in sitemap.xml has a meta description between 70 and 160 characters.
4. Standalone status pages (e.g. 404.qmd) also carry valid titles and descriptions.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.check_quarto_render_coverage import load_sitemap_paths, sitemap_loc_to_source_path
from src.tools.utils.frontmatter import split_frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent


def get_effective_page_title(fm: dict[str, object], body: str) -> str:
    """Extract page title from YAML title, pagetitle, or first level-1 heading."""
    if fm.get("title"):
        return str(fm["title"]).strip()
    if fm.get("pagetitle"):
        return str(fm["pagetitle"]).strip()
    # Match markdown H1 outside code blocks
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return re.sub(r"\{#[^}]+\}", "", m.group(1)).strip()
    # Match HTML H1
    m_html = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL | re.IGNORECASE)
    if m_html:
        return re.sub(r"<[^>]+>", "", m_html.group(1)).strip()
    return ""


def get_published_sources() -> list[Path]:
    """Return all published source paths mapped from sitemap.xml."""
    sitemap_path = REPO_ROOT / "sitemap.xml"
    locs = load_sitemap_paths(sitemap_path)
    return [sitemap_loc_to_source_path(loc, REPO_ROOT) for loc in locs]


def test_home_page_title_is_descriptive() -> None:
    """Home page must use a descriptive title rather than generic 'Home'."""
    index_path = REPO_ROOT / "index.qmd"
    assert index_path.exists(), "index.qmd must exist"
    fm, _ = split_frontmatter(index_path.read_text(encoding="utf-8"))
    title = str(fm.get("title", "")).strip()

    assert title, "index.qmd must declare a title"
    assert title.lower() != "home", "Home page title must not be generic 'Home' (#4575)"
    assert "AffineDrift" in title, f"Home page title '{title}' should identify the site"


def test_every_published_page_has_non_empty_unique_title() -> None:
    """Every published page must have a non-empty and unique title across the site."""
    sources = get_published_sources()
    assert len(sources) >= 200, f"Expected full sitemap coverage; got {len(sources)} sources"

    titles_by_source: dict[Path, str] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        title = get_effective_page_title(fm, body)
        assert title, f"{source} has an empty or unresolvable title"
        titles_by_source[source] = title

    # Check uniqueness
    titles_list = list(titles_by_source.values())
    duplicates: dict[str, list[str]] = {}
    for title in set(titles_list):
        if titles_list.count(title) > 1:
            duplicates[title] = [
                str(s.relative_to(REPO_ROOT)) for s, t in titles_by_source.items() if t == title
            ]

    assert not duplicates, f"Found duplicate page titles (#4575): {duplicates}"


def test_every_published_page_has_valid_meta_description() -> None:
    """Every published page must have a description between 70 and 160 characters."""
    sources = get_published_sources()
    failures: list[str] = []

    for source in sources:
        text = source.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(text)
        desc = str(fm.get("description", "")).strip()

        if not desc:
            failures.append(f"{source.relative_to(REPO_ROOT)}: missing description")
        elif len(desc) < 70:
            failures.append(
                f"{source.relative_to(REPO_ROOT)}: description too short ({len(desc)} < 70): '{desc}'"
            )
        elif len(desc) > 160:
            failures.append(
                f"{source.relative_to(REPO_ROOT)}: description too long ({len(desc)} > 160): '{desc}'"
            )

    assert not failures, (
        f"Found {len(failures)} pages with invalid descriptions (must be 70-160 chars, #4575):\n"
        + "\n".join(failures[:20])
    )


def test_not_found_page_has_valid_title_and_description() -> None:
    """404.qmd must carry a valid title and 70-160 character description."""
    path = REPO_ROOT / "404.qmd"
    text = path.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)

    title = str(fm.get("title", "")).strip()
    desc = str(fm.get("description", "")).strip()

    assert title, "404.qmd must have a title"
    assert 70 <= len(desc) <= 160, f"404.qmd description length ({len(desc)}) must be 70-160 chars"
