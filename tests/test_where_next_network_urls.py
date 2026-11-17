"""Network-path URL regressions for footer generation and validation."""

from pathlib import Path

import pytest

from src.tools.where_next import (
    compute_relative_href,
    render_where_next_html,
    validate_where_next_config,
)


@pytest.mark.parametrize("source", ["index.qmd", "articles/nested/page.qmd"])
def test_network_path_href_is_preserved(source: str) -> None:
    """Source depth must not turn a remote URL into a local file path."""
    target = "//example.org/guide?view=full#section"
    assert compute_relative_href(source, target) == target


def test_footer_keeps_external_network_path() -> None:
    """The rendered footer retains the browser's remote URL semantics."""
    entry = {"evidence": [{"href": "//example.org/guide", "title": "Guide"}]}
    html = render_where_next_html(entry, "articles/page.qmd")
    assert 'href="//example.org/guide"' in html


def test_network_path_is_not_validated_on_disk(tmp_path: Path) -> None:
    """Remote footer links must not require a local hostname directory."""
    (tmp_path / "page.qmd").write_text("---\ntitle: Page\n---\n", encoding="utf-8")
    config = {"page.qmd": {"evidence": [{"href": "//example.org/guide", "title": "Guide"}]}}
    errors = validate_where_next_config(config, tmp_path)
    assert not any("link target does not exist" in error for error in errors)
