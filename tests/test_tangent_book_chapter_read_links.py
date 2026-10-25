"""Book page chapter read links must name their targets and match chapter topics (#5183)."""

from __future__ import annotations

import re
from pathlib import Path

from src.tools.site_page_scan import parse_front_matter

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_PAGE = REPO_ROOT / "books" / "tangent-space-methods.qmd"

_CHAPTER_SECTION = re.compile(
    r"^## Chapter (\d+):[^\n]*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)
_RESOURCE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)\{\.resource-link\}")

_SERIES_PART_TITLES: dict[str, str] = {
    Path(part)
    .with_suffix(".html")
    .name: parse_front_matter(
        (REPO_ROOT / "articles/tangent-hyperplanes-series" / part).read_text(encoding="utf-8")
    )["title"]
    for part in (
        "part-3-control.qmd",
        "part-4-residuals-curvature.qmd",
        "part-5-contraction.qmd",
        "part-6-hybrid.qmd",
    )
}

_ADVANCED_DUALITY_TITLE = parse_front_matter(
    (
        REPO_ROOT
        / "articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_Unification.qmd"
    ).read_text(encoding="utf-8")
)["title"]

_MANUSCRIPT_TITLE = parse_front_matter(
    (
        REPO_ROOT / "articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd"
    ).read_text(encoding="utf-8")
)["title"]


def _chapter_blocks() -> dict[int, str]:
    text = BOOK_PAGE.read_text(encoding="utf-8")
    return {int(match.group(1)): match.group(2) for match in _CHAPTER_SECTION.finditer(text)}


def _first_local_read_link(block: str) -> tuple[str, str]:
    for link_text, href in _RESOURCE_LINK.findall(block):
        if href.startswith("http"):
            continue
        if "Source" in link_text or "Notebook" in link_text:
            continue
        if link_text.strip().lower().startswith("read"):
            return link_text, href
    raise AssertionError(f"No local read link found in chapter block:\n{block[:200]}...")


def _href_basename(href: str) -> str:
    return Path(href.split("#", 1)[0]).name


def test_volume_i_chapter_read_links_name_targets_and_match_topics() -> None:
    """Ch.4–Ch.7 read links must open on-topic material and say what they open."""
    blocks = _chapter_blocks()
    expectations: dict[int, dict[str, object]] = {
        4: {
            "href_name": "part-5-contraction.html",
            "text_tokens": ("Part 5", "Contraction"),
            "forbidden_hrefs": ("part-4-residuals-curvature.html",),
        },
        5: {
            "href_name": "part-3-control.html",
            "text_tokens": ("Part 3", "Control"),
            "forbidden_hrefs": (),
        },
        6: {
            "href_name": "Contraction_Tangent_Unification.html",
            "text_tokens": ("Scope Limits",),
            "forbidden_hrefs": ("part-4-residuals-curvature.html",),
        },
        7: {
            "href_name": "Tangent_Hyperplanes_Unified_Thesis.html",
            "fragment": "counterfactual-decomposition",
            "text_tokens": ("Counterfactual", "manuscript"),
            "forbidden_hrefs": ("part-6-hybrid.html",),
        },
    }

    for chapter, rules in expectations.items():
        link_text, href = _first_local_read_link(blocks[chapter])
        assert (
            rules["href_name"] in href
        ), f"Ch.{chapter} href {href!r} missing {rules['href_name']!r}"
        fragment = rules.get("fragment")
        if fragment:
            assert f"#{fragment}" in href, f"Ch.{chapter} should anchor #{fragment} in {href!r}"
        for token in rules["text_tokens"]:
            assert token in link_text, f"Ch.{chapter} link text {link_text!r} missing {token!r}"
        for forbidden in rules["forbidden_hrefs"]:
            assert forbidden not in href, f"Ch.{chapter} still points at {forbidden!r}"

        basename = _href_basename(href)
        if basename in _SERIES_PART_TITLES:
            title = _SERIES_PART_TITLES[basename]
            topic_words = [word for word in title.split(":", 1)[-1].split() if len(word) > 3]
            assert any(
                word in link_text for word in topic_words
            ), f"Ch.{chapter} link text should reflect target title {title!r}"
        elif basename == "Contraction_Tangent_Unification.html":
            assert _ADVANCED_DUALITY_TITLE in link_text
        elif basename == "Tangent_Hyperplanes_Unified_Thesis.html":
            assert "Counterfactual" in link_text
            assert _MANUSCRIPT_TITLE  # referenced for future extensions


def test_tangent_summaries_do_not_overstate_linear_superposition() -> None:
    """Hub and book summaries must not claim a linear map or exact finite superposition (#5181)."""
    book = BOOK_PAGE.read_text(encoding="utf-8")
    hub = (REPO_ROOT / "pages/tangent-hyperplanes.qmd").read_text(encoding="utf-8")

    forbidden = (
        "preserve exact linear superposition",
        "fixed-state linear force-to-acceleration map",
        "the mapping from applied generalized forces to instantaneous generalized "
        "acceleration is linear",
    )
    for phrase in forbidden:
        assert phrase not in book, f"books/tangent-space-methods.qmd still contains {phrase!r}"
        assert phrase not in hub, f"pages/tangent-hyperplanes.qmd still contains {phrase!r}"

    core_claim = (
        "at fixed state, time, and mode, perturbations map linearly to the first variation "
        "of the state rate"
    )
    for text, label in ((book, "book Ch.1"), (hub, "hub intro")):
        assert core_claim in text, f"{label} must state the first-variation claim verbatim"
        assert "control-affine" in text.lower(), f"{label} must name the control-affine assumption"
        assert "affine" in text.lower(), f"{label} must describe the map as affine"
        assert (
            "perturbations map linearly to rate increments" not in text
        ), f"{label} must not drop 'first variation' from the rate-increment claim"
