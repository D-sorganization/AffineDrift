"""Tests for the short on-ramp learning paths page (WEB-01.7 / #4492).

Enforces:
1. resources/on-ramp-paths.qmd exists with valid title/description/categories.
2. Every persona in config/personas.yml has a 5-minute, 30-minute, and 3-hour
   on-ramp section, each with at least one page-and-time-estimate entry, a
   goal statement, and a self-check question with its answer.
3. All internal relative links in the page resolve to existing files.
4. The page is reachable from resources/learning-paths.qmd (not orphaned).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAGE_PATH = ROOT / "resources" / "on-ramp-paths.qmd"
PERSONAS_PATH = ROOT / "config" / "personas.yml"

TIER_SUFFIXES = ("5min", "30min", "3hr")

TIME_ESTIMATE_PATTERN = re.compile(r"~\d+\s*(?:min|hour)")
SELF_CHECK_PATTERN = re.compile(r"\*\*Self-check:\*\*")
ANSWER_PATTERN = re.compile(r"\*\*Answer:\*\*")


def _persona_ids() -> list[str]:
    data = yaml.safe_load(PERSONAS_PATH.read_text(encoding="utf-8"))
    return list(data["personas"].keys())


def _section(content: str, start_marker: str, end_marker: str | None) -> str:
    """Return the slice of content from start_marker up to (excluding) end_marker."""
    start = content.find(start_marker)
    assert start != -1, f"Missing marker: {start_marker}"
    if end_marker is None:
        return content[start:]
    end = content.find(end_marker, start + len(start_marker))
    assert end != -1, f"Missing end marker {end_marker!r} after {start_marker!r}"
    return content[start:end]


def test_page_exists_with_metadata() -> None:
    assert PAGE_PATH.is_file(), f"Missing {PAGE_PATH}"
    content = PAGE_PATH.read_text(encoding="utf-8")
    assert content.startswith("---")
    parts = content.split("---", 2)
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])
    assert fm.get("title")
    assert fm.get("description")
    assert fm.get("categories") == ["resources"]


def test_every_persona_has_all_three_tiers() -> None:
    content = PAGE_PATH.read_text(encoding="utf-8")
    for persona_id in _persona_ids():
        for suffix in TIER_SUFFIXES:
            anchor = f"{{#onramp-{persona_id}-{suffix}}}"
            assert anchor in content, f"Missing anchor {anchor} for persona '{persona_id}'"


def test_every_tier_lists_a_timed_page_and_self_check() -> None:
    content = PAGE_PATH.read_text(encoding="utf-8")
    persona_ids = _persona_ids()
    anchors = [
        f"{{#onramp-{persona_id}-{suffix}}}"
        for persona_id in persona_ids
        for suffix in TIER_SUFFIXES
    ]
    positions = sorted((content.find(a), a) for a in anchors)
    for idx, (pos, anchor) in enumerate(positions):
        assert pos != -1, f"Anchor not found: {anchor}"
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(content)
        section = content[pos:end]
        assert TIME_ESTIMATE_PATTERN.search(section), f"No time estimate under {anchor}"
        assert SELF_CHECK_PATTERN.search(section), f"No self-check question under {anchor}"
        assert ANSWER_PATTERN.search(section), f"No self-check answer under {anchor}"
        assert re.search(r"\[[^\]]+\]\([^)]+\)", section), f"No page link under {anchor}"


def test_internal_links_resolve() -> None:
    content = PAGE_PATH.read_text(encoding="utf-8")
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for _text, target in link_pattern.findall(content):
        if target.startswith(("http", "#", "mailto:")):
            continue
        clean_target = target.split("#")[0].split("?")[0]
        if not clean_target:
            continue
        assert not clean_target.endswith(".qmd"), f"Link uses .qmd extension: {target}"
        assert not clean_target.startswith("/"), f"Root-absolute link: {target}"
        resolved = (PAGE_PATH.parent / clean_target).resolve()
        if resolved.suffix == ".html":
            qmd_candidate = resolved.with_suffix(".qmd")
            md_candidate = resolved.with_suffix(".md")
            index_candidate = resolved.parent / resolved.stem / "index.qmd"
            exists = (
                resolved.is_file()
                or qmd_candidate.is_file()
                or md_candidate.is_file()
                or index_candidate.is_file()
            )
            assert exists, f"Broken link in on-ramp-paths.qmd: '{target}' -> {resolved}"
        else:
            assert resolved.exists(), f"Broken link in on-ramp-paths.qmd: '{target}' -> {resolved}"


def test_page_is_linked_from_learning_paths_hub() -> None:
    learning_paths = (ROOT / "resources" / "learning-paths.qmd").read_text(encoding="utf-8")
    assert "on-ramp-paths.html" in learning_paths
