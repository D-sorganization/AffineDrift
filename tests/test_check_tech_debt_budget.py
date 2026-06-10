"""Tests for the technical-debt marker budget gate (issue #3230)."""

from __future__ import annotations

import scripts.check_tech_debt_budget as gate
from scripts.check_tech_debt_budget import (
    MARKERS,
    count_markers,
    evaluate_tech_debt_budget,
)

# Build marker strings dynamically so this test file does not itself trip the
# tech-debt gate it is testing.
_HACK = "HA" + "CK"
_XXX = "XX" + "X"


def test_count_markers_detects_each_marker_case_insensitively():
    text = f"# {_HACK} fix later\n// {_HACK.lower()} again\nx = 1  # {_XXX}\n"
    counts = count_markers(text)
    assert counts[_HACK] == 2
    assert counts[_XXX] == 1


def test_count_markers_returns_all_markers_zeroed_when_clean():
    counts = count_markers("def f():\n    return 1\n")
    assert set(counts) == set(MARKERS)
    assert sum(counts.values()) == 0


def test_evaluate_passes_when_under_all_budgets():
    counts = {m: 0 for m in MARKERS}
    counts[_HACK] = 2
    max_per = {m: 5 for m in MARKERS}
    _details, errors = evaluate_tech_debt_budget(counts, max_total=10, max_per=max_per)
    assert errors == []


def test_evaluate_fails_on_total_overrun():
    counts = {m: 0 for m in MARKERS}
    counts[_HACK] = 9
    max_per = {m: 100 for m in MARKERS}
    _details, errors = evaluate_tech_debt_budget(counts, max_total=5, max_per=max_per)
    assert any("Total marker budget exceeded" in e for e in errors)


def test_evaluate_fails_on_per_marker_overrun():
    counts = {m: 0 for m in MARKERS}
    counts[_XXX] = 4
    max_per = {m: 100 for m in MARKERS}
    max_per[_XXX] = 1
    _details, errors = evaluate_tech_debt_budget(counts, max_total=1000, max_per=max_per)
    assert any(f"{_XXX} budget exceeded" in e for e in errors)


def test_evaluate_boundary_exactly_at_budget_passes():
    counts = {m: 0 for m in MARKERS}
    counts[_HACK] = 3
    max_per = {m: 3 for m in MARKERS}
    _details, errors = evaluate_tech_debt_budget(counts, max_total=3, max_per=max_per)
    assert errors == []


def test_evaluate_missing_per_marker_config_treats_limit_as_zero():
    counts = {m: 0 for m in MARKERS}
    counts[_HACK] = 1
    # max_per omits the HACK key entirely -> limit defaults to 0 -> violation.
    _details, errors = evaluate_tech_debt_budget(counts, max_total=1000, max_per={})
    assert any(f"{_HACK} budget exceeded" in e for e in errors)


def test_main_passes_against_real_repo():
    # Integration smoke: live config + real tree currently within budget.
    # Exercises load_config + collect_matching_files + count_markers + report.
    assert gate.main() == 0
