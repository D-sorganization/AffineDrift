"""Privacy Policy page contract (issue #4576).

`metrics.js` stores usage data only in localStorage, but nothing told readers
what is and is not collected. These tests require a page that documents local
storage, the service worker, third-party embeds, and analytics (per D6 in
docs/development/website-improvement-draft-issues-2026-09-29.md), and that the
page is linked from the site footer.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent
PRIVACY_POLICY = ROOT_DIR / "pages" / "privacy-policy.qmd"
QUARTO_CONFIG = ROOT_DIR / "_quarto.yml"


def _frontmatter(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), f"{path} is missing YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path} has malformed YAML frontmatter"
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else {}


def test_privacy_policy_page_exists_with_metadata() -> None:
    assert PRIVACY_POLICY.exists(), "pages/privacy-policy.qmd is missing"

    metadata = _frontmatter(PRIVACY_POLICY)
    assert metadata.get("title"), "privacy-policy.qmd needs a title"
    description = str(metadata.get("description", "")).strip()
    assert description, "privacy-policy.qmd needs a meta description"
    assert 50 <= len(description) <= 160


def test_privacy_policy_covers_local_storage_service_worker_embeds_and_analytics() -> None:
    text = " ".join(PRIVACY_POLICY.read_text(encoding="utf-8").split())

    # Local storage (metrics.js) coverage.
    assert "localStorage" in text or "local storage" in text.casefold()
    assert "metrics" in text.casefold()

    # Service worker / offline caching coverage.
    assert "service worker" in text.casefold()

    # Third-party embeds (YouTube video embeds, jsDelivr CDN). Fonts are
    # self-hosted since #4557, so the page must not list a font CDN.
    assert "YouTube" in text
    assert "fonts.googleapis.com" not in text
    assert "fonts.gstatic.com" not in text
    assert "self-hosted" in text.casefold()

    # Analytics coverage per D6: no third-party analytics is currently used.
    assert "analytics" in text.casefold()
    assert "third-party" in text.casefold() or "third party" in text.casefold()


def test_privacy_policy_is_linked_from_the_site_footer() -> None:
    website = yaml.safe_load(QUARTO_CONFIG.read_text(encoding="utf-8"))["website"]
    footer = website["page-footer"]
    links = {item["text"]: item["href"] for item in footer["right"]}

    assert links.get("Privacy Policy") == "pages/privacy-policy.html"
