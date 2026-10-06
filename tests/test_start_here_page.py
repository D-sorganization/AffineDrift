"""Contract of the WEB-01.1 "Start Here" page (#4486).

One plain-language entry page: what the site is, the big idea in one picture
(WEB-08.2), a card per persona, how to read the evidence labels, and what the
site is not. It must be the first navbar item and the home page's primary call
to action, carry no display equations, and score at most grade 10.
"""

from __future__ import annotations

import re

import yaml

from tests.helpers.entry_pages import (
    ROOT,
    assert_no_display_equations,
    assert_readable_hub_page,
    assert_routes_every_persona,
    headings,
    page_text,
    section,
)

PAGE_PATH = "pages/start-here.qmd"
SECTIONS = (
    "What AffineDrift Is",
    "The Big Idea in One Picture",
    "Choose Your Path",
    "How to Read the Evidence Labels",
    "What This Site Is Not",
)


def _section(title: str) -> str:
    return section(PAGE_PATH, title)


def test_sections_appear_in_the_specified_order() -> None:
    # The site link gate requires the canonical Related Articles footer last.
    assert headings(PAGE_PATH) == (*SECTIONS, "Related Articles")


def test_intro_is_three_sentences() -> None:
    body = _section(SECTIONS[0]).split("\n", 1)[1]
    prose = " ".join(line for line in body.splitlines() if line and not line.startswith(":::"))
    assert len(re.findall(r"[.!?](?=\s|$)", prose)) == 3


def test_big_idea_reuses_the_signature_graphic() -> None:
    assert "{{< include ../_includes/generated/drift-plus-control.qmd >}}" in _section(SECTIONS[1])


def test_every_persona_has_a_card_linking_to_its_on_ramp() -> None:
    personas = yaml.safe_load((ROOT / "config" / "personas.yml").read_text(encoding="utf-8"))
    cards = _section(SECTIONS[2])
    assert_routes_every_persona(cards)
    for persona_id, persona in personas["personas"].items():
        assert persona["tagline"] in cards, persona_id


def test_evidence_labels_link_to_the_canonical_definitions() -> None:
    section_text = _section(SECTIONS[3])
    assert "../pages/how-to-read.html#publication-states" in section_text
    assert "../pages/how-to-read.html#evidence-ladder" in section_text
    for state in ("Available", "Validated", "Experimental", "Planned", "Deprecated", "Opinion"):
        assert f"**{state}**" in section_text, state


def test_states_what_the_site_is_not() -> None:
    section_text = _section(SECTIONS[4]).lower()
    for phrase in ("coaching advice", "peer reviewed", "validated model of a human"):
        assert phrase in section_text, phrase


def test_has_no_display_equations() -> None:
    assert_no_display_equations(PAGE_PATH)


def test_readability_is_grade_ten_or_lower_and_checked_as_a_hub_page() -> None:
    assert_readable_hub_page(PAGE_PATH)


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
    assert "../pages/overview.html" in page_text(PAGE_PATH)
