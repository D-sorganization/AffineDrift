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


def test_no_unqualified_lowercase_input_map_notation() -> None:
    """NOTATION.md fixes the control-affine input map as G(x), uppercase.

    A lowercase g(x)u may appear only where a self-check explicitly names it
    as the notation error to catch, never as the page's own notation.
    """
    content = PAGE_PATH.read_text(encoding="utf-8")
    for line in content.splitlines():
        if "g(x)u" in line:
            assert "lowercase" in line.lower(), f"Unqualified lowercase g(x)u: {line!r}"


def test_theory_part_1_time_estimate_is_consistent() -> None:
    content = PAGE_PATH.read_text(encoding="utf-8")
    estimates = re.findall(
        r"Theory Part 1: Control-Affine Derivation\]\([^)]+\) — (~\d+\s*min)",
        content,
    )
    assert len(estimates) >= 2, "Expected multiple Theory Part 1 links to check for consistency"
    assert len(set(estimates)) == 1, f"Inconsistent Theory Part 1 time estimates: {estimates}"


def test_theory_part_4_not_described_as_double_pendulum() -> None:
    """theory-part4.qmd covers beam/pendulum derivations, not a double pendulum."""
    content = PAGE_PATH.read_text(encoding="utf-8")
    assert "double-pendulum benchmark" not in content.lower()
    for line in content.splitlines():
        if "Theory Part 4" in line:
            assert (
                "double" not in line.lower()
            ), f"Theory Part 4 line wrongly mentions a double pendulum: {line!r}"


def test_no_recall_trivia_self_checks() -> None:
    """Self-checks must be reflective, not 'per its own description' recall."""
    content = PAGE_PATH.read_text(encoding="utf-8")
    assert "per its own description" not in content.lower()


def test_subtitle_hours_match_learning_paths_hub() -> None:
    content = PAGE_PATH.read_text(encoding="utf-8")
    assert "10–160+ hours" in content
    assert "40–160 hours" not in content


THREE_HOUR_HEADING_PATTERN = re.compile(
    r"^### (\d+)(?:–(\d+))? Hours \{#onramp-([\w-]+)-3hr\}$", re.MULTILINE
)
STEP_TIME_PATTERN = re.compile(r"— ~(\d+)\s*min")


def test_three_hour_tier_totals_match_heading() -> None:
    """Each '3 Hours' (or renamed range) tier's summed step minutes must match

    its own heading: an exact 'N Hours' heading must sum to N*60 minutes, and
    a 'A–B Hours' range heading must sum to somewhere between A*60 and B*60
    minutes. This is what #4695 fixed: several '3 Hours' on-ramps only summed
    to 120-140 minutes of listed study time.
    """
    content = PAGE_PATH.read_text(encoding="utf-8")
    matches = list(THREE_HOUR_HEADING_PATTERN.finditer(content))
    persona_ids = _persona_ids()
    found_personas = {m.group(3) for m in matches}
    assert found_personas == set(persona_ids), (
        f"Expected a 3-hour heading for every persona, got {found_personas} "
        f"vs {set(persona_ids)}"
    )

    for match in matches:
        low_str, high_str, persona_id = match.groups()
        end = content.find("\n---\n", match.end())
        assert end != -1, f"No closing '---' found after {persona_id}'s 3-hour section"
        section = content[match.end() : end]
        total_minutes = sum(int(m) for m in STEP_TIME_PATTERN.findall(section))

        low = int(low_str) * 60
        high = int(high_str) * 60 if high_str else low
        assert low <= total_minutes <= high, (
            f"Persona '{persona_id}' 3-hour tier sums to {total_minutes} min, "
            f"outside heading range {low}-{high} min"
        )
