"""Render the metadata contract through real Pandoc, including invalid inputs."""

import shutil
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.integration


def render_card(metadata: str) -> BeautifulSoup:
    """Run the production Lua filter with project-relative prerequisite sources."""
    quarto = shutil.which("quarto")
    assert quarto, "Quarto is required to verify the metadata contract"
    result = subprocess.run(
        [
            quarto,
            "pandoc",
            "--from=markdown",
            "--to=html",
            "--lua-filter=scripts/filters/page-header-card.lua",
        ],
        input=f"---\n{metadata}\n---\n\nArticle body.\n",
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return BeautifulSoup(result.stdout, "html.parser")


def test_prerequisite_route_uses_source_title_and_working_site_link() -> None:
    card = render_card('prerequisites:\n  - "pages/how-to-read.html"')
    link = card.select_one(".page-header-item--prerequisites a")
    assert link is not None
    assert link["href"] == "/pages/how-to-read.html"
    assert link.get_text() == "How to Read This Site"


def test_plain_prerequisites_and_markdown_links_are_preserved() -> None:
    card = render_card(
        'prerequisites:\n  - "Basic Calculus"\n  - "[A Reference](https://example.org/reference)"'
    )
    assert "Basic Calculus" in card.get_text()
    assert card.select_one('a[href="https://example.org/reference"]').get_text() == "A Reference"


@pytest.mark.parametrize(
    "value", ["javascript:alert(1)", "//example.org/secret", "../private.html"]
)
def test_unsafe_prerequisite_targets_are_never_linked(value: str) -> None:
    card = render_card(f'prerequisites:\n  - "[Reference]({value})"')
    assert not card.select(".page-header-item--prerequisites a")


def test_title_publication_date_is_not_duplicated_in_header_card() -> None:
    card = render_card('date: "2026-09-10"\nlast-reviewed: "2026-10-01"')
    assert not card.select(".page-header-item--published")
    assert "2026-10-01" in card.select_one(".page-header-item--reviewed").get_text()


def test_standalone_publication_date_retains_honest_uncertainty() -> None:
    card = render_card('published: "unknown"\ndate-source: "unverified"')
    assert "Publication date not verified" in card.get_text()
    assert not card.select("time")


def test_publication_date_does_not_invent_a_review_date() -> None:
    card = render_card('published: "2026-09-10"')
    assert card.select_one(".page-header-item--published time")
    assert not card.select(".page-header-item--reviewed")


def test_audience_does_not_invent_a_publication_status() -> None:
    card = render_card('audience: "Beginner"')
    assert "Beginner" in card.select_one(".page-header-item--audience").get_text()
    assert not card.select(".page-header-item--maturity")


def test_citation_only_pages_do_not_get_an_empty_metadata_panel() -> None:
    card = render_card("citation: true")
    assert not card.select(".page-header-card")
    assert card.select_one('a[href="#citation"]')
    assert card.get_text().index("Article body.") < card.get_text().index("Cite this page")
