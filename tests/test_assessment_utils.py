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


def test_classify_assessment_category():
    # A: Code Structure
    assert classify_assessment_category("Assessment_A") == "Code Structure"
    assert classify_assessment_category("Report", "code structure") == "Code Structure"

    # B: Documentation
    assert classify_assessment_category("Assessment_B") == "Documentation"
    assert classify_assessment_category("Report", "missing documentation") == "Documentation"

    # C: Test Coverage
    assert classify_assessment_category("Assessment_C") == "Test Coverage"
    assert classify_assessment_category("Report", "test coverage") == "Test Coverage"

    # D: Error Handling
    assert classify_assessment_category("Assessment_D") == "Error Handling"
    assert classify_assessment_category("Report", "error handling") == "Error Handling"

    # E: Performance
    assert classify_assessment_category("Assessment_E") == "Performance"
    assert classify_assessment_category("Report", "performance bottleneck") == "Performance"

    # F: Security
    assert classify_assessment_category("Assessment_F") == "Security"
    assert classify_assessment_category("Report", "security vulnerability") == "Security"

    # G: Dependencies
    assert classify_assessment_category("Assessment_G") == "Dependencies"
    assert classify_assessment_category("Report", "dependencies") == "Dependencies"

    # H: CI/CD
    assert classify_assessment_category("Assessment_H") == "CI/CD"
    assert classify_assessment_category("Report", "ci pipeline") == "CI/CD"

    # I: Code Style
    assert classify_assessment_category("Assessment_I") == "Code Style"
    assert classify_assessment_category("Report", "code style") == "Code Style"

    # J: API Design
    assert classify_assessment_category("Assessment_J") == "API Design"
    assert classify_assessment_category("Report", "api design") == "API Design"

    # K: Data Handling
    assert classify_assessment_category("Assessment_K") == "Data Handling"
    assert classify_assessment_category("Report", "data handling") == "Data Handling"

    # L: Logging
    assert classify_assessment_category("Assessment_L") == "Logging"
    assert classify_assessment_category("Report", "logging") == "Logging"

    # M: Configuration
    assert classify_assessment_category("Assessment_M") == "Configuration"
    assert classify_assessment_category("Report", "configuration") == "Configuration"

    # N: Scalability
    assert classify_assessment_category("Assessment_N") == "Scalability"
    assert classify_assessment_category("Report", "scalability") == "Scalability"

    # O: Maintainability
    assert classify_assessment_category("Assessment_O") == "Maintainability"
    assert classify_assessment_category("Report", "maintainability") == "Maintainability"

    # General
    assert classify_assessment_category("Unknown Report") == "General"
