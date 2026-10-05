"""Contract of the WEB-01.1 "Start Here" page (#4486).

One plain-language entry page: what the site is, the big idea in one picture
(WEB-08.2), a card per persona, how to read the evidence labels, and what the
site is not. It must be the first navbar item and the home page's primary call
to action, carry no display equations, and score at most grade 10.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from scripts.check_readability import (
    DEFAULT_GRADE_THRESHOLD,
    DEFAULT_HUB_PAGES,
    score_prose,
    split_frontmatter,
)

ROOT = Path(__file__).resolve().parent.parent
PAGE_PATH = "pages/start-here.qmd"
PAGE = ROOT / PAGE_PATH
SECTIONS = (
    "What AffineDrift Is",
    "The Big Idea in One Picture",
    "Choose Your Path",
    "How to Read the Evidence Labels",
    "What This Site Is Not",
)


def _text() -> str:
    """The page source."""
    return PAGE.read_text(encoding="utf-8")


def _section(title: str) -> str:
    """Body of one ``##`` section."""
    text = _text()
    start = text.index(f"## {title}")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else len(text)]


def test_sections_appear_in_the_specified_order() -> None:
    headings = re.findall(r"^## (.+?)(?: \{#[^}]+\})?$", _text(), flags=re.MULTILINE)
    # The site link gate requires the canonical Related Articles footer last.
    assert tuple(headings) == (*SECTIONS, "Related Articles")


def test_intro_is_three_sentences() -> None:
    body = _section(SECTIONS[0]).split("\n", 1)[1]
    prose = " ".join(line for line in body.splitlines() if line and not line.startswith(":::"))
    assert len(re.findall(r"[.!?](?=\s|$)", prose)) == 3


def test_big_idea_reuses_the_signature_graphic() -> None:
    assert "{{< include ../_includes/generated/drift-plus-control.qmd >}}" in _section(SECTIONS[1])


def test_every_persona_has_a_card_linking_to_its_on_ramp() -> None:
    personas = yaml.safe_load((ROOT / "config" / "personas.yml").read_text(encoding="utf-8"))
    on_ramps = (ROOT / "resources" / "on-ramp-paths.qmd").read_text(encoding="utf-8")
    cards = _section(SECTIONS[2])
    for persona_id, persona in personas["personas"].items():
        anchor = f"onramp-{persona_id.replace('_', '-')}"
        assert f"{{#{anchor}}}" in on_ramps, anchor
        assert f"../resources/on-ramp-paths.html#{anchor}" in cards, persona_id
        assert persona["name"] in cards and persona["tagline"] in cards, persona_id


def test_evidence_labels_link_to_the_canonical_definitions() -> None:
    section = _section(SECTIONS[3])
    assert "../pages/how-to-read.html#publication-states" in section
    assert "../pages/how-to-read.html#evidence-ladder" in section
    for state in ("Available", "Validated", "Experimental", "Planned", "Deprecated", "Opinion"):
        assert f"**{state}**" in section, state


def test_states_what_the_site_is_not() -> None:
    section = _section(SECTIONS[4]).lower()
    for phrase in ("coaching advice", "peer reviewed", "validated model of a human"):
        assert phrase in section, phrase


def test_has_no_display_equations() -> None:
    _, body = split_frontmatter(_text())
    assert "$$" not in body and "\\[" not in body and "\\begin{" not in body


def test_readability_is_grade_ten_or_lower_and_checked_as_a_hub_page() -> None:
    assert PAGE_PATH in DEFAULT_HUB_PAGES
    score = score_prose(split_frontmatter(_text())[1])
    assert score is not None
    assert score.grade <= DEFAULT_GRADE_THRESHOLD, score


def test_is_the_first_navbar_item() -> None:
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    first = config["website"]["navbar"]["left"][0]
    assert first == {"text": "Start Here", "href": "pages/start-here.html"}


def test_is_the_home_page_primary_call_to_action() -> None:
    home = (ROOT / "index.qmd").read_text(encoding="utf-8")
    actions = home[home.index('<div class="home-hero__actions">') :]
    first = re.search(r'<a class="([^"]+)" href="([^"]+)"', actions)
    assert first is not None
    assert first.group(1) == "site-button"
    assert first.group(2) == "pages/start-here.html"


def test_overview_is_reachable_from_start_here() -> None:
    assert "../pages/overview.html" in _text()
