"""Contract tests for the article draft "Same Motion, Different Muscles" (#4530, #5197)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import validate_article_frontmatter

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/same-motion-different-muscles/same-motion-different-muscles.qmd"
ARTICLE_REL = "articles/same-motion-different-muscles/same-motion-different-muscles.qmd"
BIB = ROOT / "articles/same-motion-different-muscles/references.bib"

SECTION_IDS = [
    "sec-plain-idea",
    "sec-null-spaces",
    "sec-beyond-kinematics",
    "sec-ahmad-setup",
    "sec-ahmad-results",
    "sec-ahmad-limits",
    "sec-fleet-connection",
    "sec-upstreamdrift-parity",
    "sec-validation-roadmap",
    "sec-checklist",
    "sec-tier4-tier5",
    "sec-related",
]
FENCE = re.compile(r"^\s*(```+|~~~+)")


def _text() -> str:
    return ARTICLE.read_text(encoding="utf-8")


def _body_lines() -> list[tuple[int, str]]:
    inside, out = False, []
    for number, line in enumerate(_text().splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            out.append((number, line))
    return out


def test_frontmatter_conforms_to_schema_and_preserves_draft_hold() -> None:
    front, _ = split_frontmatter(_text())
    assert validate_article_frontmatter(front, ARTICLE_REL) == []
    assert front["title"] == "Same Motion, Different Muscles: What Parity Actually Needs to Check"
    assert (
        front["canonical"]
        == "/articles/same-motion-different-muscles/same-motion-different-muscles.html"
    )
    assert front["draft"] is True
    assert front["evidence-rung"] == "mathematical-identity"
    assert front["status"] == "experimental"


AHMAD_NUMBERS = [
    ("H1090", r"11.88^\circ"),
    ("H1090", "r = 0.89"),
    ("H1090", "0.164"),
    ("H1090", "r = 0.40"),
    ("H1090", "0.81"),
    ("H1090", "-0.27"),
    ("H1090", "-0.08"),
    ("MM240-2D", r"14.65^\circ"),
    ("MM240-2D", "r = 0.76"),
    ("MM240-2D", "0.344"),
    ("MM240-2D", "0.11"),
    ("MM240-2D", "0.312"),
    ("MM240-2D", "0.16"),
    ("MM240-2D", "0.76"),
    ("MM240-2D", "0.70"),
    ("H-AB08", r"16.68^\circ"),
    ("H-AB08", "r = 0.80"),
    ("H-AB08", "0.192"),
    ("H-AB08", "0.20"),
    ("H2190", r"12.85^\circ"),
    ("H2190", "r = 0.88"),
    ("H2190", "0.240"),
    ("H2190", "0.26"),
    ("MM240-3D", r"18\,\text{s}"),
    ("MM240-3D", r"140\,\text{s}"),
    ("MM240-3D", r"36\,\text{h}"),
]


@pytest.mark.parametrize(("label", "token"), AHMAD_NUMBERS)
def test_ahmad_table_ii_numbers_match(label: str, token: str) -> None:
    assert token in _text(), f"{label}: {token!r} missing in article"


DISCLAIMERS = [
    r"HyFyDy-IL and MuscleMimic did not differ only in tendon elasticity",
    r"(actuator count|RL algorithm|kinematic retargeting|baseline reward function)",
    r"failed to take a single step",
    r"Internal reporting discrepancy",
    r"pooled EMG correlation of.*is an encouraging step, not ground-truth",
    r"no golfer muscle measurements|no new human golfer measurements",
    r"stripped Tier 1 rigid-body proxies",
    r"gluteus medius.*vastus lateralis.*gluteus maximus|gluteus maximus.*gluteus medius.*vastus lateralis",
]


@pytest.mark.parametrize("pattern", DISCLAIMERS)
def test_scope_disclaimer_is_present(pattern: str) -> None:
    assert re.search(pattern, _text(), re.IGNORECASE), f"Missing: {pattern}"


def test_five_tier_checklist_and_sections_present_in_order() -> None:
    text = _text()
    pos = 0
    for tier in [
        "1. Kinematics",
        "2. Joint Torques & Contact Wrenches",
        "3. Muscle Activations & Tendon State",
        "4. Mechanical Energy Flow",
        "5. Sensitivity & Jacobians",
    ]:
        idx = text.find(tier, pos)
        assert idx != -1, f"Missing tier: {tier}"
        pos = idx + len(tier)
    ids = [
        m.group(1)
        for _, line in _body_lines()
        if (m := re.match(r"^##+ .+\{#(sec-[a-z0-9-]+)\}\s*$", line))
    ]
    assert ids == SECTION_IDS


def test_citations_resolve_in_local_bibliography() -> None:
    text, bib_text = _text(), BIB.read_text(encoding="utf-8")
    for key in (
        "ahmad2026beyond",
        "scherpereel2023dataset",
        "choi2026musculoskeletal",
        "li2026musclemimic",
    ):
        assert f"@{key}" in text and key in bib_text, f"Missing citation or bib entry: {key}"
