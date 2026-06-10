"""Content-lint regression GATE for the committed wrist article — issue #3234.

Replaces the old root-level fix_html.py *repair* tool with a *detection* gate
(DbC-correct direction: fail loudly on a violation rather than silently
rewriting the artifact). If a future regeneration reintroduces the malformed
markup the patcher used to silently fix, this test fails instead.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = REPO_ROOT / "content" / "wrist-as-universal-joint" / "Wrist_Universal_Claude.html"

# Each (substring, human reason) the artifact must NOT contain.
FORBIDDEN = [
    ("</li></li>", "doubled list-item closers"),
    ("<p>\\begin{align}", "paragraph-wrapped math block"),
    ("<p>\n<ul>", "paragraph wrapper before a <ul>"),
    ("<p>\n<ol>", "paragraph wrapper before an <ol>"),
]


@pytest.mark.skipif(not ARTICLE.exists(), reason="wrist article not present")
@pytest.mark.parametrize(("needle", "reason"), FORBIDDEN)
def test_article_has_no_malformed_markup(needle: str, reason: str):
    html = ARTICLE.read_text(encoding="utf-8")
    assert needle not in html, f"Article contains {reason!r} ({needle!r}); regenerate cleanly."
