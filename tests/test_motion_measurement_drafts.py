"""Tests for MM-4 motion measurement draft articles Part 1 and Part 2 (#5412)."""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "development" / "motion-measurement"
PART1 = DOCS_DIR / "part-1-representing-orientation.qmd"
PART2 = DOCS_DIR / "part-2-joint-coordinates-velocity-consequences.qmd"

SECTIONS_P1 = ["1.1", "1.2", "1.3", "1.4", "1.5"]
SECTIONS_P2 = ["2.1", "2.2", "2.3", "2.4", "2.5"]
FIGURES_P1 = ["F1", "F2", "F3", "F4"]
FIGURES_P2 = ["F5", "F6", "F7", "F8"]

CARD_FIELDS = [
    "Frame",
    "Axes",
    "Sequence",
    "Sign",
    "Velocity component",
    "Events",
    "Units",
]

CARD_METRICS = [
    "X-factor variants",
    "X-factor stretch",
    "Shoulder and pelvis turn",
    "Kinematic sequence & speed gain",
    "Event-relative time normalisation",
    "Trunk tilt and lateral bend",
]

UD_REFS = [f"UD#{num}" for num in range(14421, 14429)]


def _split_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"Missing YAML frontmatter in {path}"
    fm = yaml.safe_load(parts[1])
    assert isinstance(fm, dict), f"Frontmatter in {path} must be a dict"
    return fm, parts[2]


def test_draft_files_exist_and_frontmatter_valid() -> None:
    for path in (PART1, PART2):
        assert path.exists(), f"File {path} does not exist"
        fm, body = _split_frontmatter(path)
        assert fm.get("draft") is True, f"{path} draft flag must be True"
        assert fm.get("listing") is False, f"{path} listing flag must be False"
        assert "title" in fm, f"{path} must have title"


def test_part1_sections_and_figures() -> None:
    _, body = _split_frontmatter(PART1)
    for sec in SECTIONS_P1:
        assert f"## {sec}" in body or f"### {sec}" in body
    for fig in FIGURES_P1:
        assert fig in body
    assert "rotation-representations-reference.qmd" in body
    assert "Chasles" in body
    assert "Woltring" in body
    assert "IMU" in body


def test_part2_sections_and_figures() -> None:
    _, body = _split_frontmatter(PART2)
    for sec in SECTIONS_P2:
        assert f"## {sec}" in body or f"### {sec}" in body
    for fig in FIGURES_P2:
        assert fig in body
    assert "Grood" in body
    assert "Wu" in body
    assert "Poisson" in body
    assert "hemisphere" in body
    assert "Kwon" in body
    assert "Brown" in body
    assert "Cheetham 2001" in body


def test_convention_cards_present_with_all_seven_fields() -> None:
    _, body = _split_frontmatter(PART2)
    for metric in CARD_METRICS:
        assert metric in body, f"Metric {metric} missing from Part 2"
    for field in CARD_FIELDS:
        matches = len(re.findall(rf"\b{field}\b(?:\*\*)*\s*:", body))
        assert matches >= len(
            CARD_METRICS
        ), f"Field {field}: expected at least {len(CARD_METRICS)} occurrences, got {matches}"


def test_upstreamdrift_registry_references_marked_pending() -> None:
    _, body = _split_frontmatter(PART2)
    for ud in UD_REFS:
        assert ud in body, f"Reference {ud} missing in Part 2"
    assert "pending" in body


def test_no_banned_citations_or_unindexed_verify_tags() -> None:
    for path in (PART1, PART2):
        text = path.read_text(encoding="utf-8")
        assert "Hum Mov Sci" not in text
        assert "Cheetham 2002" not in text
        assert "[VERIFY]" not in text
