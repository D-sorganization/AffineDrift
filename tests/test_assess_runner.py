"""Tests for scripts.assess_runner - orchestration and reporting."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.assess_runner import (
    _build_comprehensive_report,
    _calculate_final_grade,
    _run_all_assessments,
)


def _make_scores(grade: float = 7.0) -> dict:
    """Build a complete A-O scores dict with a uniform grade."""
    return {
        cat: {"grade": grade, "details": "detail", "recommendation": "rec"}
        for cat in "ABCDEFGHIJKLMNO"
    }


class TestCalculateFinalGrade:
    def test_uniform_grades(self):
        scores = _make_scores(8.0)
        grade = _calculate_final_grade(scores)
        assert abs(grade - 8.0) < 0.01

    def test_zero_scores(self):
        scores = _make_scores(0.0)
        grade = _calculate_final_grade(scores)
        assert grade == 0.0

    def test_returns_float(self):
        scores = _make_scores(5.5)
        grade = _calculate_final_grade(scores)
        assert isinstance(grade, float)

    def test_empty_scores(self):
        grade = _calculate_final_grade({})
        assert grade == 0.0


class TestBuildComprehensiveReport:
    def test_contains_overall_grade(self):
        scores = _make_scores(7.0)
        report = _build_comprehensive_report(scores, 7.0)
        assert "7.00/10" in report

    def test_contains_category_breakdown_header(self):
        scores = _make_scores(7.0)
        with patch("pathlib.Path.mkdir"):
            report = _build_comprehensive_report(scores, 7.0)
        assert "## Category Breakdown" in report
        assert "| Category | Grade | Weight |" in report

    def test_creates_issue_for_low_grade(self):
        scores = _make_scores(7.0)
        scores["A"] = {"grade": 3.0, "details": "bad", "recommendation": "fix it"}
        with patch("scripts.assess_runner.generate_issue_document") as mock_issue:
            mock_path = MagicMock()
            mock_path.name = "issue_A.md"
            mock_issue.return_value = mock_path
            with patch("pathlib.Path.mkdir"):
                report = _build_comprehensive_report(scores, 6.9)
        mock_issue.assert_called_once()
        assert "issue_A.md" in report

    def test_no_issues_for_high_grades(self):
        scores = _make_scores(8.0)
        with patch("scripts.assess_runner.generate_issue_document") as mock_issue:
            with patch("pathlib.Path.mkdir"):
                _build_comprehensive_report(scores, 8.0)
        mock_issue.assert_not_called()

    def test_ends_with_newline(self):
        scores = _make_scores(7.0)
        with patch("pathlib.Path.mkdir"):
            report = _build_comprehensive_report(scores, 7.0)
        assert report.endswith("\n")


class TestRunAllAssessments:
    @patch("scripts.assess_runner.assess_maintainability")
    @patch("scripts.assess_runner.assess_scalability")
    @patch("scripts.assess_runner.assess_configuration")
    @patch("scripts.assess_runner.assess_logging")
    @patch("scripts.assess_runner.assess_data_handling")
    @patch("scripts.assess_runner.assess_api_design")
    @patch("scripts.assess_runner.assess_code_style")
    @patch("scripts.assess_runner.assess_cicd")
    @patch("scripts.assess_runner.assess_dependencies")
    @patch("scripts.assess_runner.assess_security")
    @patch("scripts.assess_runner.assess_performance")
    @patch("scripts.assess_runner.assess_error_handling")
    @patch("scripts.assess_runner.assess_test_coverage")
    @patch("scripts.assess_runner.assess_documentation")
    @patch("scripts.assess_runner.assess_code_structure")
    def test_returns_all_15_categories(self, *mocks):
        stub = {"grade": 7.0, "details": "d", "recommendation": "r"}
        for m in mocks:
            m.return_value = stub
        scores = _run_all_assessments(Path("/tmp"), [])  # nosec B108
        assert len(scores) == 15
        for cat in "ABCDEFGHIJKLMNO":
            assert cat in scores
