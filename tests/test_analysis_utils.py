from pathlib import Path

from src.tools.utils import analysis_utils


def test_imports():
    assert analysis_utils


def test_get_python_metrics_empty():
    # Just check it returns a dict even for nonexistent or empty
    # For nonexistent it might return empty dict or raise error handled?
    # Based on code:
    # try: content = filepath.read_text...
    # except Exception: pass
    # return metrics
    metrics = analysis_utils.get_python_metrics(Path("nonexistent.py"))
    assert isinstance(metrics, dict)
    assert metrics["functions"] == 0
