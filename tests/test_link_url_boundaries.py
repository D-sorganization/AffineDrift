"""URL component regressions for local link validation."""

import pytest

from src.tools.utils.link_utils import is_external_url, normalize_internal_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("page.html?view=full#section", "page.html"),
        ("/articles/my%20page.html?download=1", "/articles/my page.html"),
        ("page%3Fname.html?view=full", "page?name.html"),
        ("?view=full#section", None),
        ("//example.org/page.html", None),
    ],
)
def test_normalize_url_components(url: str, expected: str | None) -> None:
    """Filesystem lookup uses the decoded path of local URLs only."""
    assert normalize_internal_url(url) == expected


def test_network_path_is_external() -> None:
    """A protocol-relative host is external even without an explicit scheme."""
    assert is_external_url("//example.org/page.html")


def test_root_relative_path_remains_local() -> None:
    """A single leading slash continues to denote a site-local path."""
    assert not is_external_url("/articles/page.html")
