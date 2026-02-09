from src.tools.utils import html_utils

def test_imports():
    assert html_utils

def test_escape_html():
    assert html_utils.escape_html("<script>") == "&lt;script&gt;"
    assert html_utils.escape_html("&") == "&amp;"
