"""Tests for report utilities."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

from src.tools.utils import report_utils


def test_generate_markdown_report(tmp_path):
    """Test generating a markdown report."""
    output_dir = tmp_path / "assessments"
    report_utils.generate_markdown_report(
        category_id="A",
        category_name="Test Category",
        grade=9.5,
        details="Test details.",
        recommendations=["Rec 1", "Rec 2"],
        output_dir=output_dir,
    )

    expected_file = output_dir / "Assessment_A_Test_Category.md"
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert "# Assessment: Test Category" in content
    assert "Grade: 9.5/10" in content
    assert "Test details." in content
    assert "- Rec 1" in content
    assert "- Rec 2" in content


def test_generate_markdown_report_default_recs(tmp_path):
    """Test generating report with default recommendations."""
    output_dir = tmp_path / "assessments"
    report_utils.generate_markdown_report(
        category_id="B",
        category_name="Another Category",
        grade=5.0,
        details="Details.",
        output_dir=output_dir,
    )

    expected_file = output_dir / "Assessment_B_Another_Category.md"
    content = expected_file.read_text(encoding="utf-8")
    assert "- See detailed findings" in content


def test_generate_issue_document(tmp_path):
    """Test generating an issue document."""
    output_dir = tmp_path / "issues"
    report_utils.generate_issue_document(
        category_id="C",
        category_name="Low Score Category",
        grade=3.0,
        details="Bad things found.",
        output_dir=output_dir,
    )

    expected_file = output_dir / "ISSUE_Assessment_C_Low_Score_Category.md"
    assert expected_file.exists()

    content = expected_file.read_text(encoding="utf-8")
    assert 'title: "Assessment Finding: Low Score in Low Score Category"' in content
    assert "labels: jules:assessment, needs-attention" in content
    assert "Grade**: 3.0/10" in content
    assert "Bad things found." in content
