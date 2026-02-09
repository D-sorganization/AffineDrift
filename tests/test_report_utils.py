from src.tools.utils import report_utils

def test_imports():
    assert report_utils

def test_generate_markdown_report_signature():
    # Just check function exists
    assert hasattr(report_utils, "generate_markdown_report")
