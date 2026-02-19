import pytest

from src.tools.utils import html_utils


def test_imports():
    assert html_utils


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("<script>", "&lt;script&gt;"),
        ("&", "&amp;"),
        ('"quoted"', "&quot;quoted&quot;"),
        ("'single'", "&#x27;single&#x27;"),
        ("plain text", "plain text"),
        ("", ""),
        ("<div class='x'>", "&lt;div class=&#x27;x&#x27;&gt;"),
    ],
)
def test_escape_html(text: str, expected: str):
    assert html_utils.escape_html(text) == expected
