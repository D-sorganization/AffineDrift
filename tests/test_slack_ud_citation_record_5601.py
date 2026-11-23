"""Guard the UpstreamDrift citation record for the two Slack articles (Refs #5601).

The record ``docs/development/technical-review/ud-citation-verification-5601-slack.md``
states that every UpstreamDrift permalink in the Slack articles was checked against
its pinned commit. This test fails if an article gains, drops or re-pins a permalink
without the record being updated, so the claim cannot silently go stale.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/development/technical-review/ud-citation-verification-5601-slack.md"
ARTICLES = (
    ROOT / "articles/slack-management-linked-systems.qmd",
    ROOT / "articles/slack-takeup-identifiability.qmd",
)
UD_LINK = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:blob|tree)/([0-9a-f]{40})/([^)#\s\"]+)"
)


def _article_links() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for article in ARTICLES:
        found.update(UD_LINK.findall(article.read_text(encoding="utf-8")))
    return found


def test_record_exists() -> None:
    assert RECORD.is_file()


def test_articles_use_only_full_length_commit_pins() -> None:
    for article in ARTICLES:
        text = article.read_text(encoding="utf-8")
        assert "UpstreamDrift/blob/main" not in text
        assert "UpstreamDrift/tree/main" not in text


def test_every_article_permalink_is_recorded_with_its_pin() -> None:
    record = RECORD.read_text(encoding="utf-8")
    links = _article_links()
    assert links, "expected UpstreamDrift permalinks in the Slack articles"
    missing = [
        f"{sha[:8]} {path}"
        for sha, path in sorted(links)
        if f"{sha[:8]}" not in record or path not in record
    ]
    assert not missing, f"permalinks not covered by the verification record: {missing}"


def test_record_documents_the_var05_discrepancy() -> None:
    record = RECORD.read_text(encoding="utf-8")
    assert "VAR-05" in record
    assert "Impedance is declared, not measured" in record
