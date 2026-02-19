import pytest

from src.tools.utils import assessment_utils
from src.tools.utils.assessment_utils import classify_assessment_category


def test_categories_exist():
    assert assessment_utils.CATEGORIES
    assert "A" in assessment_utils.CATEGORIES
    assert "O" in assessment_utils.CATEGORIES


def test_group_weights():
    assert assessment_utils.GROUP_WEIGHTS
    # Weights sum to 1.0 (with floating point tolerance)
    assert abs(sum(assessment_utils.GROUP_WEIGHTS.values()) - 1.0) < 1e-6


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Assessment_A", "Code Structure"),
        ("Assessment_B", "Documentation"),
        ("Assessment_C", "Test Coverage"),
        ("Assessment_D", "Error Handling"),
        ("Assessment_E", "Performance"),
        ("Assessment_F", "Security"),
        ("Assessment_G", "Dependencies"),
        ("Assessment_H", "CI/CD"),
        ("Assessment_I", "Code Style"),
        ("Assessment_J", "API Design"),
        ("Assessment_K", "Data Handling"),
        ("Assessment_L", "Logging"),
        ("Assessment_M", "Configuration"),
        ("Assessment_N", "Scalability"),
        ("Assessment_O", "Maintainability"),
    ],
)
def test_classify_by_source_prefix(source: str, expected: str):
    assert classify_assessment_category(source) == expected


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("code structure", "Code Structure"),
        ("missing documentation", "Documentation"),
        ("test coverage", "Test Coverage"),
        ("error handling", "Error Handling"),
        ("performance bottleneck", "Performance"),
        ("security vulnerability", "Security"),
        ("dependencies", "Dependencies"),
        ("ci pipeline", "CI/CD"),
        ("code style", "Code Style"),
        ("api design", "API Design"),
        ("data handling", "Data Handling"),
        ("logging", "Logging"),
        ("configuration", "Configuration"),
        ("scalability", "Scalability"),
        ("maintainability", "Maintainability"),
    ],
)
def test_classify_by_description(description: str, expected: str):
    assert classify_assessment_category("Report", description) == expected


def test_classify_unknown_returns_general():
    assert classify_assessment_category("Unknown Report") == "General"
