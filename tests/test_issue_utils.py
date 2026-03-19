from src.tools.utils import issue_utils
from src.tools.utils.issue_utils import format_issue_body


def test_imports():
    assert issue_utils


def test_get_repo_short_name():
    name = issue_utils.get_repo_short_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_format_issue_body_returns_markdown_string() -> None:
    """format_issue_body should return a formatted Markdown string."""
    body = format_issue_body(
        severity="HIGH",
        category="testing",
        source="test_source",
        description="Something broke",
        timestamp="2026-03-01",
    )
    assert "HIGH" in body
    assert "testing" in body
    assert "Something broke" in body


def test_format_issue_body_includes_severity_and_category() -> None:
    """format_issue_body should include severity and category in output."""
    body = format_issue_body(
        severity="CRITICAL",
        category="coverage",
        source="CI",
        description="Coverage dropped",
    )
    assert "CRITICAL" in body
    assert "coverage" in body
