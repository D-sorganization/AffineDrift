import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add scripts directory to path
scripts_dir = str(Path(__file__).parents[1] / "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import assess_repo  # noqa: E402


def test_get_python_files():
    """Test finding python files."""
    files = assess_repo.get_python_files(Path.cwd())
    assert len(files) > 0
    # Ensure this test file is found (since it's a python file not in ignored dirs)
    assert any("test_assess_repo.py" in str(f) for f in files)


def test_assess_code_structure_basic():
    """Test code structure assessment logic."""
    mock_file = MagicMock()
    # 10 lines
    mock_file.read_text.return_value = "print('hello')\n" * 10
    # Depth 2
    mock_file.relative_to.return_value.parts = ["a", "b"]

    result = assess_repo.assess_code_structure([mock_file])
    assert result["grade"] == 10
    assert "Avg LOC" in result["details"]


def test_assess_documentation_mock():
    """Test documentation assessment with mocked content."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = '''
def my_func():
    """This is a docstring."""
    return True

class MyClass:
    """Class docstring."""
    pass
'''
    result = assess_repo.assess_documentation([mock_file])
    # 2 defs, 2 docstrings => 100% coverage => grade 10 (ignoring README bonus)
    # The README bonus adds 1 if > 5 READMEs found.
    # Base score is coverage/10 = 10.
    # Max grade is 10.
    assert result["grade"] == 10
    assert "100.0%" in result["details"]


def test_assess_error_handling_mock():
    """Test error handling assessment."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = """
try:
    pass
except Exception:
    pass
"""
    result = assess_repo.assess_error_handling([mock_file])
    # 1 try, 0 bare except (except Exception is not bare in the regex check? regex is "except\s*:")
    # The regex r"except\s*:" matches "except:" or "except :" but NOT "except Exception:"
    # So 0 bare excepts.
    # Score start 7. Bare except count 0. Try count 1 (which is <= 20).
    # Score = 7.
    assert result["grade"] == 7
