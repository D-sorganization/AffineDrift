from src.tools.utils import issue_utils


def test_imports():
    assert issue_utils

def test_get_repo_short_name():
    name = issue_utils.get_repo_short_name()
    assert isinstance(name, str)
    assert len(name) > 0
