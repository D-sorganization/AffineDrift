"""Contract of the WEB-01.4 "The Big Idea in Five Minutes" page (#4489).

A short, equation-free explainer of drift versus control, the zero-torque
counterfactual and the drift-control ratio, built on everyday analogies. Each
analogy says where it breaks, at most one symbolic expression sits inside an
optional "In symbols" box, the reader can try the drift-versus-control sandbox,
and the page ends by routing each persona onward. It is linked from Start Here,
the home page and the top of Theory Part 1.
"""

from __future__ import annotations

import re

import pytest

from tests.helpers.entry_pages import (
    assert_no_display_equations,
    assert_readable_hub_page,
    assert_routes_every_persona,
    headings,
    page_body,
    page_text,
    section,
)

PAGE_PATH = "pages/big-idea.qmd"
PAGE_URL = "big-idea.html"
ANALOGIES = (
    "A Swing on a Playground",
    "A Thrown Ball and a Pushed Ball",
    "What If the Golfer Stopped Pushing?",
)
SECTIONS = (
    "Two Arrows at Every Moment",
    *ANALOGIES,
    "How Big Is the Push?",
    "Try It Yourself",
    "Where to Go Next",
)
SANDBOX = "../articles/theory-part1.html#drift-control-sandbox"
BREAKS = '::: {.callout-caution title="Where the analogy breaks"}'
IN_SYMBOLS = '::: {.callout-note collapse="true" title="In symbols"}'


def _prose_words() -> int:
    """Words a reader sees: the body without shortcodes, HTML, fences or link targets."""
    body = page_body(PAGE_PATH)
    body = re.sub(r"\{\{<.*?>\}\}", " ", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\]\([^)]*\)", "]", body)
    body = re.sub(r"\{[^}]*\}", " ", body)
    body = re.sub(r"^:::.*$", " ", body, flags=re.MULTILINE)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", body))


def test_title_names_the_page() -> None:
    assert 'title: "The Big Idea in Five Minutes"' in page_text(PAGE_PATH)


def test_sections_appear_in_order_with_related_articles_last() -> None:
    assert headings(PAGE_PATH) == (*SECTIONS, "Related Articles")


def test_reads_in_about_five_minutes() -> None:
    assert 800 <= _prose_words() <= 1200, _prose_words()


@pytest.mark.parametrize("title", ANALOGIES)
def test_every_analogy_says_where_it_breaks(title: str) -> None:
    assert BREAKS in section(PAGE_PATH, title)


def test_has_no_display_equations() -> None:
    assert_no_display_equations(PAGE_PATH)


def test_at_most_one_symbolic_expression_and_only_inside_the_symbols_box() -> None:
    body = page_body(PAGE_PATH)
    expressions = re.findall(r"(?<!\\)\$[^$\n]+\$", body)
    assert len(expressions) <= 1, expressions
    if expressions:
        box = body[body.index(IN_SYMBOLS) :]
        box = box[: box.index("\n:::\n")]
        assert expressions[0] in box


def test_counterfactual_and_ratio_link_to_their_definitions() -> None:
    text = page_text(PAGE_PATH)
    assert "../articles/zero-torque-counterfactual.html" in text
    assert "../articles/drift-control-ratio.html" in text
    assert "../pages/glossary.html#zero-torque-counterfactual" in text
    assert "../pages/glossary.html#drift-control-ratio" in text


def test_ratio_is_described_as_a_capacity_not_a_share_of_motion() -> None:
    ratio = section(PAGE_PATH, "How Big Is the Push?").lower()
    assert "can be bigger than one" in ratio
    assert "not" in ratio and "share of the motion" in ratio


def test_try_it_links_the_drift_versus_control_sandbox() -> None:
    assert SANDBOX in section(PAGE_PATH, "Try It Yourself")


def test_where_to_go_next_routes_every_persona() -> None:
    assert_routes_every_persona(section(PAGE_PATH, "Where to Go Next"))


def test_readability_is_grade_ten_or_lower_and_checked_as_a_hub_page() -> None:
    assert_readable_hub_page(PAGE_PATH)


def test_linked_from_start_here() -> None:
    assert f"../pages/{PAGE_URL}" in section("pages/start-here.qmd", "The Big Idea in One Picture")


def test_reachable_through_the_home_page_primary_action() -> None:
    home = page_text("index.qmd")
    hero = home[home.index('<section id="welcome"') : home.index("</section>")]
    assert 'href="pages/start-here.html"' in hero
    assert f"../pages/{PAGE_URL}" in section("pages/start-here.qmd", "The Big Idea in One Picture")


def test_linked_from_the_top_of_theory_part_one() -> None:
    body = page_body("articles/theory-part1.qmd")
    assert f"../pages/{PAGE_URL}" in body[: body.index("\n## ")]
