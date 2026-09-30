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


def test_biomechanics_schedule_no_overlap() -> None:
    path_page = REPO_ROOT / "resources" / "learning-path-biomechanics.qmd"
    text = path_page.read_text(encoding="utf-8")
    assert "parallel with Module 7" not in text, "Biomechanics Modules 7 and 8 should not overlap"
    m7_match = re.search(r"## Module 7[^\n]*\n\*\*Weeks\s*([0-9–]+)", text)
    m8_match = re.search(r"## Module 8[^\n]*\n\*\*Weeks\s*([0-9–]+)", text)
    assert m7_match and m8_match
    assert m7_match.group(1) != m8_match.group(1), "Module 7 and Module 8 weeks must be distinct"
