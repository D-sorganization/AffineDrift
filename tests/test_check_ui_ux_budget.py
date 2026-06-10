"""Tests for the UI/UX anti-pattern budget gate (issue #3230)."""

from __future__ import annotations

import scripts.check_ui_ux_budget as gate
from scripts.check_ui_ux_budget import compile_checks, evaluate_ui_ux_budget

_CHECK_CONFIG = {
    "inline_event_handlers": {"pattern": r"\bon[a-z]+\s*=", "max_count": 1},
    "inline_style_attributes": {"pattern": r"\sstyle\s*=\s*[\"']", "max_count": 2},
}


def test_compile_checks_compiles_pattern_and_budget():
    compiled = compile_checks(_CHECK_CONFIG)
    assert set(compiled) == {"inline_event_handlers", "inline_style_attributes"}
    assert compiled["inline_event_handlers"]["max_count"] == 1
    # regex usable
    assert compiled["inline_event_handlers"]["regex"].findall('<a onclick="x">')


def test_evaluate_passes_when_under_budget():
    compiled = compile_checks(_CHECK_CONFIG)
    counts = {"inline_event_handlers": 1, "inline_style_attributes": 2}
    _details, errors = evaluate_ui_ux_budget(counts, compiled)
    assert errors == []


def test_evaluate_fails_when_over_budget():
    compiled = compile_checks(_CHECK_CONFIG)
    counts = {"inline_event_handlers": 5, "inline_style_attributes": 0}
    _details, errors = evaluate_ui_ux_budget(counts, compiled)
    assert any("inline_event_handlers budget exceeded" in e for e in errors)


def test_evaluate_boundary_exactly_at_budget_passes():
    compiled = compile_checks(_CHECK_CONFIG)
    counts = {"inline_event_handlers": 1, "inline_style_attributes": 2}
    _details, errors = evaluate_ui_ux_budget(counts, compiled)
    assert errors == []


def test_evaluate_missing_count_treated_as_zero():
    compiled = compile_checks(_CHECK_CONFIG)
    _details, errors = evaluate_ui_ux_budget({}, compiled)
    assert errors == []


def test_evaluate_details_include_each_check():
    compiled = compile_checks(_CHECK_CONFIG)
    details, _errors = evaluate_ui_ux_budget({"inline_event_handlers": 0}, compiled)
    assert any("inline_event_handlers" in d for d in details)
    assert any("inline_style_attributes" in d for d in details)


def test_main_passes_against_real_repo():
    # Integration smoke: live config + real tree currently within budget.
    assert gate.main() == 0
