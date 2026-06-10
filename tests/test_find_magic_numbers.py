"""Behavioral tests for ``scripts/find_magic_numbers.py`` (issue #3230).

Loaded via importlib because ``scripts`` is a flat directory of CLI utilities.
Covers: positive detection of uncited quantitative claims, the citation
suppression path, comment/math skipping, and the multi-line ``scan_lines``
aggregation (1-based line numbers).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "find_magic_numbers.py"


@pytest.fixture(scope="module")
def fmn():
    spec = importlib.util.spec_from_file_location("find_magic_numbers_under_test", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_uncited_physical_quantity_is_flagged(fmn) -> None:
    assert fmn.line_has_uncited_claim("The clubhead reaches 100 mph at impact.")


def test_uncited_study_phrase_is_flagged(fmn) -> None:
    assert fmn.line_has_uncited_claim("A study found this to be significant.")


def test_cited_quantity_is_not_flagged(fmn) -> None:
    assert not fmn.line_has_uncited_claim("The clubhead reaches 100 mph [@Smith2020].")


def test_latex_cite_suppresses_flag(fmn) -> None:
    assert not fmn.line_has_uncited_claim(r"Torque was 50 Nm \citep{Jones2019}.")


def test_comment_line_is_skippable(fmn) -> None:
    assert fmn.line_is_skippable("% 100 mph comment")
    assert fmn.line_is_skippable("<!-- 100 mph html comment -->")


def test_math_and_backslash_lines_are_skippable(fmn) -> None:
    assert fmn.line_is_skippable("$$ x = 100 mph $$")
    assert fmn.line_is_skippable(r"\section{100 mph}")


def test_plain_prose_without_quantity_is_not_flagged(fmn) -> None:
    assert not fmn.line_has_uncited_claim("The golfer swings the club smoothly.")


def test_scan_lines_returns_one_based_line_numbers(fmn) -> None:
    lines = [
        "Intro paragraph with no claims.\n",
        "The force was 50 N here.\n",  # line 2, flagged
        "% 200 N in a comment\n",  # skipped
        "Researchers confirmed the effect.\n",  # line 4, flagged
    ]
    findings = fmn.scan_lines(lines)
    line_numbers = [num for num, _ in findings]
    assert line_numbers == [2, 4]


def test_scan_lines_empty_input(fmn) -> None:
    assert fmn.scan_lines([]) == []
