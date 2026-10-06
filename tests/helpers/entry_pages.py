"""Shared contract checks for plain-language entry pages (#4486, #4489).

Start Here and The Big Idea in Five Minutes are both reader-entry pages: they
carry no display equations, score at most grade 10 as hub pages, and route each
persona in ``config/personas.yml`` to its on-ramp anchor.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from scripts.check_readability import (
    DEFAULT_GRADE_THRESHOLD,
    DEFAULT_HUB_PAGES,
    score_prose,
)
from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[2]
ON_RAMPS = "resources/on-ramp-paths.qmd"


def page_text(rel_path: str) -> str:
    """Source of the page at ``rel_path``."""
    return (ROOT / rel_path).read_text(encoding="utf-8")


def page_body(rel_path: str) -> str:
    """Source of the page without its YAML front matter."""
    return split_frontmatter(page_text(rel_path))[1]


def headings(rel_path: str) -> tuple[str, ...]:
    """The page's ``##`` headings in order, without their anchors."""
    found = re.findall(r"^## (.+?)(?: \{#[^}]+\})?$", page_text(rel_path), flags=re.MULTILINE)
    return tuple(found)


def section(rel_path: str, title: str) -> str:
    """Body of the ``##`` section titled ``title``, up to the next ``##``."""
    text = page_text(rel_path)
    if f"## {title}" not in text:
        raise ValueError(f"{rel_path} has no section {title!r}")
    start = text.index(f"## {title}")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else len(text)]


def assert_no_display_equations(rel_path: str) -> None:
    """The page body holds no display maths in any delimiter."""
    body = page_body(rel_path)
    for delimiter in ("$$", "\\[", "\\begin{"):
        assert delimiter not in body, f"{rel_path} has display maths ({delimiter})"


def assert_readable_hub_page(rel_path: str) -> None:
    """The page is scanned as a hub page and scores at most the grade threshold."""
    assert rel_path in DEFAULT_HUB_PAGES, f"{rel_path} is not a readability hub page"
    score = score_prose(page_body(rel_path))
    assert score is not None
    assert score.grade <= DEFAULT_GRADE_THRESHOLD, score


def assert_routes_every_persona(text: str) -> None:
    """``text`` names every persona and links to its on-ramp anchor."""
    personas = yaml.safe_load((ROOT / "config" / "personas.yml").read_text(encoding="utf-8"))
    on_ramps = page_text(ON_RAMPS)
    for persona_id, persona in personas["personas"].items():
        anchor = f"onramp-{persona_id.replace('_', '-')}"
        assert f"{{#{anchor}}}" in on_ramps, anchor
        assert f"../resources/on-ramp-paths.html#{anchor}" in text, persona_id
        assert persona["name"] in text, persona_id
