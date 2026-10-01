"""Tests for the 404 page's contact channel (WEB-01.10 / #4495).

Acceptance criteria covered here:
- The contact address on the 404 page matches the Contact page.

The "Start Here" and "the Library" links called for in the full WEB-01.10
proposal depend on pages that do not exist yet in this repository: the
"Start Here" page is #4486 (tier:strong, still open) and the "Library"
navbar grouping is part of the WEB-02.1 navbar restructure (also
tier:strong, unmerged). Linking to those targets now would produce dead
links, so this change is scoped to the contact-address fix; see the PR's
Blocked section for the rest.

Note: as of #4593, About no longer publishes its own mailto contact
channel — Contact is the single contact page, and About links to it
instead (see tests/test_contact_channel_unification.py).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOT_FOUND_PATH = ROOT / "404.qmd"
CONTACT_PATH = ROOT / "pages" / "contact.qmd"

EMAIL_PATTERN = re.compile(r'mailto:([^"\'?]+)')


def _first_email(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = EMAIL_PATTERN.search(content)
    assert match is not None, f"No mailto link found in {path}"
    return match.group(1)


def test_404_contact_address_matches_contact_page() -> None:
    assert _first_email(NOT_FOUND_PATH) == _first_email(CONTACT_PATH)


def test_404_does_not_use_personal_gmail_address() -> None:
    content = NOT_FOUND_PATH.read_text(encoding="utf-8")
    assert "gmail.com" not in content
