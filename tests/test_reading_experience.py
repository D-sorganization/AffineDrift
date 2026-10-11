"""Owner review #4998: focused entry paths and consistent evidence semantics."""

from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup

from scripts.check_readability import DEFAULT_GRADE_THRESHOLD, score_prose

ROOT = Path(__file__).resolve().parents[1]


def source(path: str) -> str:
    """Read a repository fixture without consulting generated output."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_has_one_action_and_concise_introduction() -> None:
    home = BeautifulSoup(source("index.qmd"), "html.parser")
    actions = home.select(".home-hero__actions a")
    assert len(actions) == 1
    assert actions[0]["href"] == "pages/start-here.html"
    assert len(home.select_one(".home-hero__lede").get_text().split()) <= 40
    assert home.select_one('a[href="books/index.html"]')
    assert home.select_one('a[href="resources/articles.html"]')


def test_featured_reading_has_no_duplicate_book_entries() -> None:
    home = BeautifulSoup(source("index.qmd"), "html.parser")
    assert "Featured Reading" in [h.get_text() for h in home.select("h2")]
    assert "Latest Writing" not in home.get_text()
    for route in (
        "articles/The_Physics_of_Golf/quarto/index.html",
        "articles/The_Geometry_of_Motion/quarto/index.html",
        "articles/proximal_distal_energy_transfer/index.html",
    ):
        assert len(home.select(f'a[href="{route}"]')) == 1


def test_start_here_offers_three_goals_then_specialist_paths() -> None:
    text = source("pages/start-here.qmd")
    choices = text.split("## Choose Your Path", 1)[1].split("\n## ", 1)[0]
    assert choices.count("::: {.resource-card}") == 3
    for title in ("Understand the Science", "Study the Mathematics", "Explore Models"):
        assert title in choices
    assert "../resources/on-ramp-paths.html" in choices
    assert "Specialist Reading Paths" in choices


def test_evidence_definitions_have_one_shared_authority() -> None:
    include = "../_includes/generated/publication-states.qmd"
    for page in ("pages/start-here.qmd", "pages/how-to-read.qmd"):
        assert f"{{{{< include {include} >}}}}" in source(page)
        assert "Nobody outside has checked it yet" not in source(page)
    definitions = source("_includes/generated/publication-states.qmd")
    assert "does not imply independent peer review" in definitions.lower()
    for state in ("Available", "Validated", "Experimental", "Planned", "Deprecated", "Opinion"):
        assert definitions.count(f"**{state}**") == 1


def test_start_here_stays_readable_with_shared_definitions_expanded() -> None:
    text = source("pages/start-here.qmd").split("---", 2)[2]
    text = text.replace(
        "{{< include ../_includes/generated/publication-states.qmd >}}",
        source("_includes/generated/publication-states.qmd"),
    )
    score = score_prose(text)
    assert score is not None and score.grade <= DEFAULT_GRADE_THRESHOLD


@pytest.mark.parametrize(
    "page", ["index.qmd", "pages/start-here.qmd", "pages/how-to-read.qmd", "resources/articles.qmd"]
)
def test_navigation_pages_do_not_export_the_entire_scholarly_bibliography(page: str) -> None:
    meta = yaml.safe_load(source(page).split("---", 2)[1])
    assert meta.get("google-scholar") is False
