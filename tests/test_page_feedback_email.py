"""Tests for page-feedback fallback email and public mailto target compliance (#5202)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_page_feedback_fallback_email_is_dashboard_affinedrift() -> None:
    js_file = ROOT / "js" / "page-feedback.js"
    content = js_file.read_text(encoding="utf-8")
    match = re.search(r'const\s+FALLBACK_EMAIL\s*=\s*["\']([^"\']+)["\']', content)
    assert match is not None, "FALLBACK_EMAIL constant must be defined in js/page-feedback.js"
    email = match.group(1)
    assert email == "dashboard@affinedrift.com", f"Expected dashboard@affinedrift.com, got {email}"
    assert "dieterolson" not in email


def test_js_directory_has_no_personal_email_addresses() -> None:
    js_dir = ROOT / "js"
    for js_file in js_dir.glob("*.js"):
        content = js_file.read_text(encoding="utf-8")
        assert (
            "dieterolson@gmail.com" not in content
        ), f"Personal email found in {js_file.relative_to(ROOT)}"
