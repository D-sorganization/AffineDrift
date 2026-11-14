"""Tests for learning path consistency and chapter references (issue #4493).

Enforces:
1. Difficulty, duration, and prerequisites match between config/learning_paths.yml,
   resources/learning-paths.qmd, and each individual learning path page.
2. Foundations prerequisites do not contradict (no "No prerequisites assumed" when
   algebra/trig are required).
3. 3Blue1Brown is not listed twice in Foundations Module 1.
4. Golf Science Module 1 links to the correct chapters (ch28, ch19, ch31) via relative anchors.
5. Biomechanics schedule has no overlapping module weeks.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "learning_paths.yml"
HUB_PAGE = REPO_ROOT / "resources" / "learning-paths.qmd"


@pytest.fixture(scope="module")
def learning_paths_config() -> dict:
    assert CONFIG_PATH.exists(), f"Missing {CONFIG_PATH}"
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert "paths" in data
    return data["paths"]


def test_config_exists_and_contains_core_paths(learning_paths_config: dict) -> None:
    expected_paths = {"foundations", "control-theory", "biomechanics", "golf-science"}
    assert set(learning_paths_config.keys()) == expected_paths


def test_hub_table_matches_config(learning_paths_config: dict) -> None:
    assert HUB_PAGE.exists()
    content = HUB_PAGE.read_text(encoding="utf-8")

    # Match rows like: | Goal | [Title](href) | Duration | Difficulty |
    row_re = re.compile(
        r"\|\s*([^|]+?)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    )
    rows = row_re.findall(content)
    hub_paths = {}
    for goal, title, href, duration, difficulty in rows:
        if "Path" in title or "---" in title:
            continue
        hub_paths[href] = {
            "goal": goal.strip(),
            "title": title.strip(),
            "duration": duration.strip(),
            "difficulty": difficulty.strip(),
        }

    for path_key, expected in learning_paths_config.items():
        href = expected["href"]
        assert href in hub_paths, f"Path {href} missing from hub table"
        actual = hub_paths[href]
        assert actual["difficulty"] == expected["difficulty"], (
            f"Difficulty mismatch for {path_key}: "
            f"hub has '{actual['difficulty']}', config has '{expected['difficulty']}'"
        )
        assert actual["duration"] == expected["duration"], (
            f"Duration mismatch for {path_key}: "
            f"hub has '{actual['duration']}', config has '{expected['duration']}'"
        )


def test_individual_pages_match_config(learning_paths_config: dict) -> None:
    for expected in learning_paths_config.values():
        page_path = REPO_ROOT / expected["source"]
        assert page_path.exists(), f"Source file {page_path} missing"
        text = page_path.read_text(encoding="utf-8")

        # Check Total Time
        time_match = re.search(r"\*\*Total Time:\*\*\s*([^|]+?)\s*\|", text)
        assert time_match, f"Could not find Total Time in {page_path}"
        actual_time = time_match.group(1).strip()
        normalized_time = actual_time.replace("hours", "hrs")
        assert (
            normalized_time == expected["duration"]
        ), f"Total time mismatch in {page_path}: expected {expected['duration']}, got {actual_time}"

        # Check Difficulty
        diff_match = re.search(r"\*\*Difficulty:\*\*\s*([^|]+?)\s*\|", text)
        assert diff_match, f"Could not find Difficulty in {page_path}"
        actual_diff = diff_match.group(1).strip()
        assert (
            actual_diff == expected["difficulty"]
        ), f"Difficulty mismatch in {page_path}: expected {expected['difficulty']}, got {actual_diff}"


def test_foundations_no_contradictory_prerequisites() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-foundations.qmd"
    text = path_page.read_text(encoding="utf-8")
    assert (
        "No prerequisites assumed" not in text
    ), "Foundations subtitle contradicts its stated prerequisite of algebra and trigonometry"
    assert "algebra and trigonometry" in text.lower()


def test_foundations_no_duplicate_3blue1brown() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-foundations.qmd"
    text = path_page.read_text(encoding="utf-8")
    # Count occurrences in Module 1
    m1_text = text.split("## Module 2:")[0]
    count = len(re.findall(r"3blue1brown", m1_text, re.IGNORECASE))
    assert count <= 2, f"3Blue1Brown is duplicated in Foundations Module 1: found {count} mentions"


def test_golf_science_module_1_correct_chapter_links() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-golf-science.qmd"
    text = path_page.read_text(encoding="utf-8")
    assert (
        "The Physics of Golf** Chapters 1–3" not in text
    ), "Golf Science Module 1 incorrectly references Physics of Golf Chapters 1–3 for impact/aerodynamics"
    assert "ch28" in text, "Golf Science Module 1 should link to ch28 (impact collision)"
    assert "ch19" in text, "Golf Science Module 1 should link to ch19 (aerodynamic drag)"
    assert "ch31" in text, "Golf Science Module 1 should link to ch31 (launch/trajectory)"


def test_resources_pinocchio_link_not_parked_domain() -> None:
    websites = REPO_ROOT / "resources" / "resources-websites.qmd"
    text = websites.read_text(encoding="utf-8")
    assert "pinocchio.org" not in text
    assert "stack-of-tasks.github.io/pinocchio" in text


def test_golf_science_no_misleading_chapter_titles() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-golf-science.qmd"
    text = path_page.read_text(encoding="utf-8")
    assert "Multibody Impact Dynamics & Oblique Collision" not in text
    assert "Personalized coaching using AffineDrift principles" not in text
    assert "ch11_flexible_shaft" in text
    assert "ch30_kinetic_chain" in text


def test_biomechanics_schedule_no_overlap() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-biomechanics.qmd"
    text = path_page.read_text(encoding="utf-8")
    assert "parallel with Module 7" not in text, "Biomechanics Modules 7 and 8 should not overlap"
    m7_match = re.search(r"## Module 7[^\n]*\n\*\*Weeks\s*([0-9–]+)", text)
    m8_match = re.search(r"## Module 8[^\n]*\n\*\*Weeks\s*([0-9–]+)", text)
    assert m7_match and m8_match
    assert m7_match.group(1) != m8_match.group(1), "Module 7 and Module 8 weeks must be distinct"


def _parse_range(spec: str) -> tuple[int, int]:
    parts = [int(p) for p in re.split(r"[–-]", spec)]
    return (parts[0], parts[-1]) if parts else (0, 0)


@pytest.mark.parametrize(
    ("filename", "expected_range"),
    [
        ("learning-path-control-theory.qmd", (120, 160)),
        ("learning-path-biomechanics.qmd", (100, 140)),
    ],
)
def test_16_week_learning_paths_weekly_schedules_match_totals(
    filename: str, expected_range: tuple[int, int]
) -> None:
    text = (REPO_ROOT / "resources" / filename).read_text(encoding="utf-8")
    assert "A 16-week " in text
    assert "over 16 weeks" in text
    assert "## Recommended Daily Schedule" not in text
    sched = text.split("## Recommended Weekly Schedule")[1].split("\n## ")[0]
    assert "/day" not in sched
    blocks = re.split(r"\n### Weeks ", sched)[1:]
    assert len(blocks) == 8, f"{filename} expected 8 two-week blocks, got {len(blocks)}"
    total_lo, total_hi = 0, 0
    for blk in blocks:
        items = re.findall(r"-\s+\*\*(?!Total:)[^:]+:\*\*\s+(\d+(?:[–-]\d+)?)\s+hours?/week", blk)
        assert items, blk[:60]
        comp_lo = sum(_parse_range(x)[0] for x in items)
        comp_hi = sum(_parse_range(x)[1] for x in items)
        tot_m = re.search(r"-\s+\*\*Total:\*\*\s+(\d+(?:[–-]\d+)?)\s+hours/week", blk)
        assert tot_m, blk[:60]
        b_lo, b_hi = _parse_range(tot_m.group(1))
        assert (comp_lo, comp_hi) == (
            b_lo,
            b_hi,
        ), f"{filename}: {(comp_lo, comp_hi)} != {(b_lo, b_hi)}"
        total_lo += 2 * b_lo
        total_hi += 2 * b_hi
    assert (total_lo, total_hi) == expected_range
    mod_hours = [
        _parse_range(m)
        for m in re.findall(r"\*\*Weeks\s+\d+[–-]\d+\s+\|\s+(\d+(?:[–-]\d+)?)\s+hours\*\*", text)
    ]
    assert len(mod_hours) == 8
    assert (sum(x[0] for x in mod_hours), sum(x[1] for x in mod_hours)) == expected_range


def test_5618_prior_citation_and_pedagogy_locks() -> None:
    assert "by Ville Hirvonen" in (REPO_ROOT / "resources" / "resources-books.qmd").read_text(
        encoding="utf-8"
    )
    assert "On Contraction Analysis for Non-linear Systems" in (
        REPO_ROOT / "resources" / "resources-books.qmd"
    ).read_text(encoding="utf-8")
    assert "10.1016/0021-9290(93)90084-R" in (
        REPO_ROOT / "resources" / "resources-papers.qmd"
    ).read_text(encoding="utf-8")
    assert "Comparing against a real recorded dataset checks whether" not in (
        REPO_ROOT / "resources" / "on-ramp-paths.qmd"
    ).read_text(encoding="utf-8")
    assert "Chapters 3 and 8" in (
        REPO_ROOT / "resources" / "learning-path-foundations.qmd"
    ).read_text(encoding="utf-8")
    ct = (REPO_ROOT / "resources" / "learning-path-control-theory.qmd").read_text(encoding="utf-8")
    assert "Chapters 13–14" in ct and "Contraction analysis (Lohmiller–Slotine)" in ct
    bio = (REPO_ROOT / "resources" / "learning-path-biomechanics.qmd").read_text(encoding="utf-8")
    assert "Wolpert & Ghahramani (2000)" in bio and "Soh & Bhatnagar" not in bio
