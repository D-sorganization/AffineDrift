from src.tools.utils import constants


def test_imports():
    assert constants

def test_exclude_dirs():
    assert constants.EXCLUDE_DIRS
    assert ".git" in constants.EXCLUDE_DIRS_PYTHON
    assert "docs" in constants.EXCLUDE_DIRS_CONTENT
