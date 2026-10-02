"""Tests for 404 page content, navigation, and contact alignment (WEB-01.10 #4495).

Validates that:
1. 404.qmd exists with compliant SEO metadata (70-160 char description, valid title).
2. The page links to 'Start Here' (/resources/learning-paths.html).
3. The page links to 'Library' (/books/index.html).
4. The page provides an explicit link or trigger for 'search'.
5. The contact address is dieterolson@AffineDrift.com matching pages/contact.qmd.
6. All target destination links in 404.qmd resolve to real source files on disk.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE_404 = REPO_ROOT / "404.qmd"
CONTACT_PAGE = REPO_ROOT / "pages" / "contact.qmd"


def _read_404() -> tuple[dict[str, Any], str]:
    """Parse frontmatter and return (frontmatter_dict, body_text)."""
    assert PAGE_404.is_file(), f"404 page not found at {PAGE_404}"
    raw = PAGE_404.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    assert len(parts) >= 3, "404.qmd must contain YAML frontmatter"
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2]
    return frontmatter, body


def test_404_metadata_conformance() -> None:
    """404 page must have valid title and description within bounds."""
    fm, _body = _read_404()
    assert fm.get("title") == "Page Not Found"
    desc = fm.get("description", "")
    assert 70 <= len(desc) <= 160, f"Description length {len(desc)} not in 70-160 chars"
    assert fm.get("toc") is False
    assert fm.get("page-layout") == "full"


def test_404_links_start_here() -> None:
    """404 page must link to Start Here / Learning Paths."""
    _fm, body = _read_404()
    # Must link to learning-paths
    assert "/resources/learning-paths.html" in body or "resources/learning-paths.html" in body
    # Link text must include 'Start Here'
    link_pattern = re.compile(
        r'<a\s+[^>]*href="[^"]*learning-paths\.html"[^>]*>([^<]*)</a>',
        re.IGNORECASE,
    )
    match = link_pattern.search(body)
    assert match is not None, "Missing link to learning-paths.html"
    assert "start here" in match.group(1).lower()


def test_404_links_library() -> None:
    """404 page must link to the Library / Books index."""
    _fm, body = _read_404()
    assert "/books/index.html" in body or "books/index.html" in body
    link_pattern = re.compile(
        r'<a\s+[^>]*href="[^"]*books/index\.html"[^>]*>([^<]*)</a>',
        re.IGNORECASE,
    )
    match = link_pattern.search(body)
    assert match is not None, "Missing link to books/index.html"
    assert "library" in match.group(1).lower()


def test_404_links_search() -> None:
    """404 page must provide an explicit search link or trigger."""
    _fm, body = _read_404()
    search_link = re.search(
        r'<a\s+[^>]*href="[^"]*search[^"]*"[^>]*>[^<]*search[^<]*</a>',
        body,
        re.IGNORECASE,
    )
    assert search_link is not None, "404 page must contain an explicit link for search"


def test_404_contact_address_matches_contact_page() -> None:
    """Contact address on 404 page must match pages/contact.qmd."""
    _fm, body_404 = _read_404()
    assert CONTACT_PAGE.is_file(), f"Contact page not found at {CONTACT_PAGE}"
    contact_text = CONTACT_PAGE.read_text(encoding="utf-8")

    emails_404 = set(
        re.findall(r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", body_404)
    )
    emails_contact = set(
        re.findall(r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", contact_text)
    )

    assert "dieterolson@AffineDrift.com" in emails_404
    assert emails_404.issubset(emails_contact)


def test_404_internal_links_exist_on_disk() -> None:
    """Every internal root-relative link on the 404 page must correspond to a real file."""
    _fm, body = _read_404()
    internal_links = re.findall(r'href="(/[a-zA-Z0-9_/-]+\.html)"', body)
    assert len(internal_links) >= 5, "404 page should suggest at least 5 destination routes"

    for link in internal_links:
        # Convert /resources/articles.html -> resources/articles.qmd or resources/articles.html
        rel_path = link.lstrip("/")
        qmd_equiv = REPO_ROOT / rel_path.replace(".html", ".qmd")
        html_equiv = REPO_ROOT / rel_path
        assert qmd_equiv.is_file() or html_equiv.is_file(), f"Link {link} does not exist on disk"
