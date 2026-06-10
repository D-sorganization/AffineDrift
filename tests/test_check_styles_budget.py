"""Tests for the CSS budget CI gate (scripts/check_styles_budget.py) — issue #3230."""

from scripts.check_styles_budget import (
    count_important,
    count_lines,
    evaluate_budget,
)


class TestCountImportant:
    def test_counts_each_important(self):
        css = ".a { color: red !important; }\n.b { width: 1px !important; }\n"
        assert count_important(css) == 2

    def test_zero_when_absent(self):
        assert count_important(".a { color: red; }") == 0


class TestCountLines:
    def test_trailing_newline_not_double_counted(self):
        assert count_lines("a\nb\n") == 2

    def test_no_trailing_newline(self):
        assert count_lines("a\nb") == 2

    def test_single_line(self):
        assert count_lines("a") == 1


class TestEvaluateBudget:
    def test_passes_when_under_budget(self):
        assert evaluate_budget(100, 2, max_lines=3400, max_important=10) == []

    def test_exactly_at_budget_passes(self):
        # Boundary: a count equal to the budget is allowed.
        assert evaluate_budget(3400, 10, max_lines=3400, max_important=10) == []

    def test_line_budget_exceeded_reports(self):
        errors = evaluate_budget(3401, 0, max_lines=3400, max_important=10)
        assert len(errors) == 1
        assert "Line budget exceeded" in errors[0]

    def test_important_budget_exceeded_reports(self):
        errors = evaluate_budget(10, 11, max_lines=3400, max_important=10)
        assert len(errors) == 1
        assert "!important budget exceeded" in errors[0]

    def test_both_exceeded_reports_two(self):
        errors = evaluate_budget(9999, 99, max_lines=3400, max_important=10)
        assert len(errors) == 2
