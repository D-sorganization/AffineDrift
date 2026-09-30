"""Contract test for the accessibility statement page (issue #4568).

Acceptance criteria (WEB-09.8): a page stating the conformance target,
known issues (linked to #4139), and a contact route for barriers.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages" / "accessibility.qmd"
KNOWN_ISSUES_URL = "https://github.com/D-sorganization/AffineDrift/issues/4139"


def _front_matter(text: str) -> dict[str, object]:
    _, front_matter, _ = text.split("---\n", 2)
    return yaml.safe_load(front_matter)


def test_page_exists_with_site_information_category() -> None:
    front = _front_matter(PAGE.read_text(encoding="utf-8"))
    assert front["categories"] == ["site-information"]


def test_page_states_a_conformance_target() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert "WCAG 2.1 Level AA" in text


def test_page_links_known_issues_to_the_tracking_issue() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert KNOWN_ISSUES_URL in text


def test_page_does_not_present_the_closed_tracking_issue_as_the_live_status() -> None:
    """Issue #4139 closed as remediated on 2026-09-06; the page must say so, and its
    description of the CI axe check must match the mode ci-standard.yml actually runs
    (issue #4691)."""
    text = PAGE.read_text(encoding="utf-8")
    lowered = " ".join(text.casefold().split())
    workflow = (ROOT / ".github/workflows/ci-standard.yml").read_text(encoding="utf-8")
    modes = set(re.findall(r"--axe (warn|fail)\b", workflow))
    assert len(modes) == 1, f"expected one axe mode in ci-standard.yml, found {modes}"

    assert "closed as remediated" in lowered
    assert "https://github.com/D-sorganization/AffineDrift/issues/4561" in text
    if modes == {"fail"}:
        assert "fails the build on any serious or critical finding" in lowered
        assert "report-only" not in lowered
    else:
        assert "report-only" in lowered


def test_page_provides_a_contact_route_for_barriers() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert "contact.html" in text
    assert "mailto:" in text


def test_page_has_a_related_articles_section_with_enough_links() -> None:
    text = PAGE.read_text(encoding="utf-8")
    _, _, related = text.partition("## Related Articles")
    assert related, "missing Related Articles section"
    assert related.count("](") >= 3


def test_footer_links_the_accessibility_statement() -> None:
    data = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    footer_links = {item["text"]: item["href"] for item in data["website"]["page-footer"]["right"]}
    assert footer_links["Accessibility"] == "pages/accessibility.html"
