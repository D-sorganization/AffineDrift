from pathlib import Path

import pytest
import yaml

from src.tools.utils import report_utils
from src.tools.utils.report_utils import AssessmentFinding, generate_report_from_finding


def test_imports():
    assert report_utils


def test_generate_markdown_report_signature():
    # Just check function exists
    assert hasattr(report_utils, "generate_markdown_report")


def test_generate_report_from_finding_writes_file(tmp_path: Path) -> None:
    """generate_report_from_finding should create a markdown file using the finding."""
    finding = AssessmentFinding(
        category_id="T",
        category_name="Testing",
        grade=4.5,
        details="Coverage is below threshold.",
        recommendations=["Write more tests", "Increase coverage"],
    )
    result = generate_report_from_finding(finding, output_dir=tmp_path)
    assert result.exists()
    content = result.read_text(encoding="utf-8")
    assert "Testing" in content
    assert "4.5" in content


@pytest.mark.parametrize(
    "category_name", ['A "quoted" name', r"Path\name", "Line\nbreak", "Tab\tname"]
)
def test_issue_title_round_trips_yaml(tmp_path: Path, category_name: str) -> None:
    """Issue metadata preserves literal characters without breaking YAML."""
    result = report_utils.generate_issue_document("T", category_name, 4.5, "Details", tmp_path)
    frontmatter = result.read_text(encoding="utf-8").split("---", 2)[1]
    assert (
        yaml.safe_load(frontmatter)["title"] == f"Assessment Finding: Low Score in {category_name}"
    )
