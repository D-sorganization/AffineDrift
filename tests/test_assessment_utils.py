from src.tools.utils import assessment_utils


def test_categories_exist():
    assert assessment_utils.CATEGORIES
    assert "A" in assessment_utils.CATEGORIES
    assert "O" in assessment_utils.CATEGORIES


def test_group_weights():
    assert assessment_utils.GROUP_WEIGHTS
    # Weights sum to 1.0 (with floating point tolerance)
    assert abs(sum(assessment_utils.GROUP_WEIGHTS.values()) - 1.0) < 1e-6
