"""Content-lint gate for the wrist article HTML (issue #3234).

This replaces the old root-level ``fix_html.py`` post-render *patcher*. Instead
of silently rewriting malformed HTML after the fact, this gate fails loudly when
the committed artifact contains the patterns the patcher used to repair, so the
artifact must be born clean (DbC: detect the violation, do not paper over it).

Marked ``content_lint`` so it is deselected from the fast default lane and run
explicitly via ``pytest -m content_lint`` (mirrors the existing
``test_geometry_of_motion_*`` content checks).
"""

from __future__ import annotations

from pathlib import Path

import pytest

ARTICLE = (
    Path(__file__).resolve().parents[1]
    / "content"
    / "wrist-as-universal-joint"
    / "Wrist_Universal_Claude.html"
)

# (pattern, human-readable explanation) — the exact malformations the legacy
# fix_html.py used to repair. A non-zero count is a hard failure.
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("</li></li>", "duplicated list-item closer (run upstream generator clean)"),
    (r"<p>\begin{align}", "paragraph-wrapped align math block"),
    (r"<p>\begin{quote}", "paragraph-wrapped quote block"),
    ("<p>\n<ul>", "stray paragraph wrapper before unordered list"),
    ("<p>\n<ol>", "stray paragraph wrapper before ordered list"),
    ("<ul></li>", "malformed list opener with stray item closer"),
    ("<ol></li>", "malformed list opener with stray item closer"),
]


@pytest.mark.content_lint
def test_wrist_article_exists():
    assert ARTICLE.is_file(), f"expected committed article at {ARTICLE}"


@pytest.mark.content_lint
@pytest.mark.parametrize("pattern,reason", FORBIDDEN_PATTERNS)
def test_wrist_article_has_no_malformed_html(pattern: str, reason: str):
    content = ARTICLE.read_text(encoding="utf-8")
    count = content.count(pattern)
    assert count == 0, (
        f"{ARTICLE.name} contains {count} occurrence(s) of {pattern!r} "
        f"({reason}). Fix the generator output rather than post-patching."
    )
