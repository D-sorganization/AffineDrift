"""Contract tests for the Seat and the Pedals article (Epic #5909, WP-1)."""

from __future__ import annotations

import re
from pathlib import Path

import jsonschema
import pytest

from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import (
    SCHEMA_PATH,
    load_article_frontmatter_schema,
    validate_article_frontmatter,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE = "articles/the-seat-and-the-pedals-drift-and-control.qmd"
COMPANIONS = (
    "affine-nature-golf-swing",
    "drift-is-the-past-control-is-the-present",
    "inverse-dynamics",
    "inverse-dynamics-inference",
    "zero-torque-counterfactual",
    "theory-part1",
    "core-theses-registry",
)
INCLUDE = "{{< include ../_includes/control-affine-attribution-boundary.qmd >}}"
COLLAPSIBLE = '::: {.callout-note collapse="true" title="In symbols"}'
SUMMARY_WORD_LIMIT = 60


@pytest.fixture(scope="module")
def parts() -> tuple[dict, str]:
    """Return (front matter, body) of the article."""
    return split_frontmatter((REPO_ROOT / ARTICLE).read_text(encoding="utf-8"))


def test_front_matter_satisfies_schema(parts: tuple[dict, str]) -> None:
    fm, _ = parts
    schema = load_article_frontmatter_schema(SCHEMA_PATH)
    assert not list(jsonschema.Draft202012Validator(schema).iter_errors(fm))
    cfg = {"core_pages": [ARTICLE], "allowlist": []}
    assert validate_article_frontmatter(fm, ARTICLE, allowlist_config=cfg) == []
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fm["date"]))
    assert len(fm["summary-plain"].split()) <= SUMMARY_WORD_LIMIT
    assert 3 <= len(fm["key-takeaways"]) <= 5


@pytest.mark.parametrize("slug", COMPANIONS)
def test_companion_link_present_and_resolves(parts: tuple[dict, str], slug: str) -> None:
    _, body = parts
    assert f"]({slug}.html)" in body
    assert (REPO_ROOT / "articles" / f"{slug}.qmd").is_file()


def test_boundary_include_collapsible_and_hook(parts: tuple[dict, str]) -> None:
    _, body = parts
    assert INCLUDE in body
    assert (REPO_ROOT / "_includes/control-affine-attribution-boundary.qmd").is_file()
    assert COLLAPSIBLE in body
    assert COLLAPSIBLE in (REPO_ROOT / "pages/big-idea.qmd").read_text(encoding="utf-8")
    assert body.lstrip().startswith("The light turns green.")


def test_citations_resolve_in_bibliography(parts: tuple[dict, str]) -> None:
    _, body = parts
    keys = set(re.findall(r"@([A-Za-z][\w:-]*\d\w*)", body))
    bib = (REPO_ROOT / "references/affine-drift.bib").read_text(encoding="utf-8")
    assert keys, "article must cite references"
    missing = [k for k in keys if not re.search(r"@\w+\{" + re.escape(k) + ",", bib)]
    assert not missing, missing
