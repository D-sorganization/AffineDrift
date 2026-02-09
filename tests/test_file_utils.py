from pathlib import Path

from src.tools.utils import file_utils


def test_imports():
    assert file_utils

def test_get_python_files():
    files = file_utils.get_python_files(".")
    assert isinstance(files, list)
    # Ensure it returns Path objects
    if files:
        assert isinstance(files[0], Path)
