"""Tests for unifying the contact channel and splitting About from Contact (#4593).

Acceptance criteria covered here:
- One contact address everywhere (About, Contact, 404 all agree).
- About is retitled away from "About & Contact" now that Contact is a
  separate page.
- Contact is the single contact page: About no longer hosts its own
  mailto contact channel and instead points readers to Contact.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABOUT_PATH = ROOT / "pages" / "about.qmd"
CONTACT_PATH = ROOT / "pages" / "contact.qmd"
NOT_FOUND_PATH = ROOT / "404.qmd"

EMAIL_PATTERN = re.compile(r'mailto:([^"\'?]+)')


def _emails(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    return EMAIL_PATTERN.findall(content)


def test_about_page_is_retitled_away_from_about_and_contact() -> None:
    about = ABOUT_PATH.read_text(encoding="utf-8")

    assert 'title: "About & Contact"' not in about
    assert "About &amp; Contact" not in about
    assert "About & Contact" not in about


def test_about_page_has_no_mailto_contact_channel() -> None:
    """Contact is the single contact page; About should not duplicate it."""

    assert _emails(ABOUT_PATH) == []


def test_about_page_points_readers_to_the_contact_page() -> None:
    about = ABOUT_PATH.read_text(encoding="utf-8")

    assert "contact.html" in about


def test_contact_page_is_the_single_source_of_the_contact_address() -> None:
    contact_emails = set(_emails(CONTACT_PATH))
    not_found_emails = set(_emails(NOT_FOUND_PATH))

    assert contact_emails, "Contact page must publish a contact address"
    assert contact_emails == not_found_emails
    assert len(contact_emails) == 1
