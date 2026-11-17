"""Boundary and render-selection tests for Quarto page discovery."""

from pathlib import Path

import pytest

from src.tools.site_page_scan import is_rendered, rendered_relative_paths


@pytest.mark.parametrize("document", ["[]", "[articles/*.qmd]", "true", "42", "plain text"])
def test_non_mapping_document_has_no_render_filter(tmp_path: Path, document: str) -> None:
    """Valid YAML without a project mapping uses the unrestricted fallback."""
    (tmp_path / "_quarto.yml").write_text(document, encoding="utf-8")
    assert rendered_relative_paths(tmp_path) is None


def test_render_patterns_keep_inclusions_and_exclusions(tmp_path: Path) -> None:
    """A structured project still filters pages and honors exclusions."""
    (tmp_path / "_quarto.yml").write_text(
        'project:\n  render:\n    - "articles/**/*.qmd"\n    - "!articles/drafts/*.qmd"\n',
        encoding="utf-8",
    )
    render_set = rendered_relative_paths(tmp_path)
    assert is_rendered("articles/page.qmd", render_set)
    assert is_rendered("articles/nested/page.qmd", render_set)
    assert not is_rendered("articles/drafts/page.qmd", render_set)
    assert not is_rendered("books/page.qmd", render_set)
