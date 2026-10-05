"""Content gates for the "In Layman's Terms" blocks (WEB-01.9, #4494).

1. At least 15 core pages render a block. A block on a page whose front matter
   sets ``summary-plain`` or ``key-takeaways`` is removed by
   ``scripts/filters/summary-takeaways.lua`` (WEB-03.3), so it does not count.
2. Every block is at most 250 words and at most Flesch-Kincaid grade 10,
   scored by ``scripts/check_readability.py`` (WEB-12.1 lay-block target).
3. Every block links at least one site glossary term instead of defining it
   inline, and every link names a declared glossary key.
4. The tangent-series ``*_LAYMAN`` explanations are linked from the lay block
   of the article they accompany.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.check_readability import extract_lay_blocks, score_prose
from src.tools.site_glossary import load_glossary
from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[1]
MIN_RENDERED_PAGES = 15
MAX_WORDS = 250
MAX_GRADE = 10.0
GLOSSARY_LINK_RE = re.compile(r'href="/pages/glossary\.html#([a-z0-9-]+)"')
SUPPRESSING_FIELDS = ("summary-plain", "key-takeaways")
TANGENT = "articles/tangent-hyperplane-articles/Advanced"
#: Each accessible tangent-series explanation and the article it accompanies.
LAYMAN_VARIANTS = {
    f"{TANGENT}/Contraction_Tangent_Unification.qmd": "Contraction_Tangent_LAYMAN.html",
    f"{TANGENT}/Hybrid_Tangent_Spaces.qmd": "Hybrid_Tangent_LAYMAN.html",
    f"{TANGENT}/Residual-Aware_Control.qmd": "Residual-Aware_Control_LAYMAN.html",
}
_EXCLUDED_DIRS = {"node_modules", "_site", ".quarto", ".git", "docs"}


def _lay_pages() -> dict[str, str]:
    """Relative path -> text for every ``.qmd`` that uses the shared component."""
    pages = {}
    for path in sorted(ROOT.rglob("*.qmd")):
        if _EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        if "::: {.laymans-terms}" in text:
            pages[path.relative_to(ROOT).as_posix()] = text
    return pages


def _renders_block(text: str) -> bool:
    front_matter, _ = split_frontmatter(text)
    return not any(front_matter.get(field) for field in SUPPRESSING_FIELDS)


def _block(text: str) -> str:
    blocks = extract_lay_blocks(text)
    assert len(blocks) == 1, "use exactly one lay block per page"
    return blocks[0]


LAY_PAGES = _lay_pages()


def test_lay_blocks_render_on_enough_core_pages() -> None:
    rendered = [path for path, text in LAY_PAGES.items() if _renders_block(text)]
    assert len(rendered) >= MIN_RENDERED_PAGES, rendered


@pytest.mark.parametrize("path", sorted(LAY_PAGES))
def test_lay_block_meets_the_readability_target(path: str) -> None:
    score = score_prose(_block(LAY_PAGES[path]))
    assert score is not None
    assert score.word_count <= MAX_WORDS, f"{path}: {score.word_count} words"
    assert score.grade <= MAX_GRADE, f"{path}: grade {score.grade:.1f}"


@pytest.mark.parametrize("path", sorted(LAY_PAGES))
def test_lay_block_links_glossary_terms(path: str) -> None:
    keys = GLOSSARY_LINK_RE.findall(_block(LAY_PAGES[path]))
    assert keys, f"{path}: link at least one term to /pages/glossary.html#<key>"
    unknown = sorted(set(keys) - set(load_glossary()))
    assert unknown == [], f"{path}: unknown glossary keys {unknown}"


@pytest.mark.parametrize(("path", "variant"), sorted(LAYMAN_VARIANTS.items()))
def test_tangent_layman_variants_are_linked_from_the_lay_block(path: str, variant: str) -> None:
    assert path in LAY_PAGES, f"{path} needs a lay block"
    assert f'href="{variant}"' in _block(LAY_PAGES[path])
