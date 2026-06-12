"""Tests for the CSS bundler that flattens the @import waterfall (issue #3219).

The canonical ``styles.css`` keeps its modular ``@import`` graph for authoring
and for ``check_css_architecture.py``. The bundler inlines that graph into a
single render-blocking ``docs/styles.css`` so browsers fetch one stylesheet
instead of a 26-request, 3-level-deep waterfall.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.bundle_css import (
    bundle,
    collect_import_graph,
    extract_imports,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestExtractImports:
    """Tests for parsing @import statements."""

    def test_parses_bare_string_import(self):
        assert extract_imports('@import "css/tokens/design-tokens.css";') == [
            "css/tokens/design-tokens.css"
        ]

    def test_parses_url_import(self):
        assert extract_imports('@import url("css/breakpoints.css");') == ["css/breakpoints.css"]

    def test_ignores_non_import_lines(self):
        assert extract_imports("body { color: red; }") == []

    def test_multiple_imports(self):
        css = '@import "a.css";\n@import url("b.css");\n'
        assert extract_imports(css) == ["a.css", "b.css"]


class TestCollectImportGraph:
    """Tests for resolving the recursive import graph relative to each file."""

    def test_resolves_relative_to_importing_file(self, tmp_path: Path):
        (tmp_path / "css" / "tokens").mkdir(parents=True)
        (tmp_path / "styles.css").write_text(
            '@import "css/tokens/tokens.css";\nbody{color:red}\n', encoding="utf-8"
        )
        # Nested import is relative to css/tokens/, not repo root.
        (tmp_path / "css" / "tokens" / "tokens.css").write_text(
            '@import url("colors.css");\n', encoding="utf-8"
        )
        (tmp_path / "css" / "tokens" / "colors.css").write_text(":root{--x:1}\n", encoding="utf-8")

        graph = collect_import_graph(tmp_path / "styles.css", tmp_path)
        # All three files participate.
        assert (tmp_path / "css" / "tokens" / "colors.css") in graph

    def test_missing_import_raises(self, tmp_path: Path):
        (tmp_path / "styles.css").write_text('@import "nope.css";\n', encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            collect_import_graph(tmp_path / "styles.css", tmp_path)


class TestBundle:
    """Tests for the flattened bundle output."""

    def test_bundle_has_no_imports(self, tmp_path: Path):
        (tmp_path / "leaf.css").write_text(":root{--leaf:1}\n", encoding="utf-8")
        (tmp_path / "styles.css").write_text(
            '@import "leaf.css";\nbody{color:var(--leaf)}\n', encoding="utf-8"
        )
        out = bundle(tmp_path / "styles.css", tmp_path)
        assert "@import" not in out

    def test_bundle_inlines_imported_rules(self, tmp_path: Path):
        (tmp_path / "leaf.css").write_text(".leaf{color:green}\n", encoding="utf-8")
        (tmp_path / "styles.css").write_text(
            '@import "leaf.css";\nbody{color:red}\n', encoding="utf-8"
        )
        out = bundle(tmp_path / "styles.css", tmp_path)
        assert ".leaf{color:green}" in out
        assert "body{color:red}" in out

    def test_bundle_is_deterministic(self, tmp_path: Path):
        (tmp_path / "leaf.css").write_text(".leaf{color:green}\n", encoding="utf-8")
        (tmp_path / "styles.css").write_text('@import "leaf.css";\n', encoding="utf-8")
        assert bundle(tmp_path / "styles.css", tmp_path) == bundle(
            tmp_path / "styles.css", tmp_path
        )


class TestRealRepoBundle:
    """Contract tests against the actual repository stylesheet."""

    def test_real_bundle_has_zero_imports(self):
        """The flattened bundle must contain no @import statements."""
        out = bundle(REPO_ROOT / "styles.css", REPO_ROOT)
        assert "@import" not in out

    def test_real_bundle_defines_color_primary_dark(self):
        """Token variables from the deepest import level survive flattening."""
        out = bundle(REPO_ROOT / "styles.css", REPO_ROOT)
        assert "--color-primary-dark" in out

    def test_real_bundle_contains_every_imported_file_marker(self):
        """Every file in the import graph contributes content to the bundle.

        Walks the recursive @import graph and asserts a recognizable substring
        from each imported file appears in the flattened output, proving no
        previously-@imported rules were dropped.
        """
        graph = collect_import_graph(REPO_ROOT / "styles.css", REPO_ROOT)
        out = bundle(REPO_ROOT / "styles.css", REPO_ROOT)
        for path in graph:
            text = path.read_text(encoding="utf-8")
            # Find a selector/declaration line that is not an @import or comment.
            marker = _significant_line(text)
            assert marker is None or marker in out, f"missing content from {path}"

    def test_real_bundle_includes_legacy_and_token_palettes(self):
        """Both the styles.css base rules and token files are present."""
        out = bundle(REPO_ROOT / "styles.css", REPO_ROOT)
        assert "--color-neutral-0" in out  # from css/tokens/colors.css
        assert "box-sizing: border-box" in out  # from styles.css base reset

    def test_real_bundle_has_no_var_in_media_preludes(self):
        """Regression for #3326: var() in a @media prelude is invalid CSS.

        Such a query parses as ``not all`` and is silently dropped by every
        browser, so the entire mobile layout never applies. The shipped bundle
        must contain zero real ``@media ... var(...)`` rules. Comment bodies
        (which document the px-literal convention) are stripped first.
        """
        out = bundle(REPO_ROOT / "styles.css", REPO_ROOT)
        decommented = re.sub(r"/\*.*?\*/", " ", out, flags=re.DOTALL)
        offenders = re.findall(r"@media[^{]*\bvar\(", decommented)
        assert offenders == [], f"invalid var() in @media prelude: {offenders}"


def _significant_line(css: str) -> str | None:
    """Return the first substantive (non-import, non-comment) line, if any."""
    in_comment = False
    for raw in css.splitlines():
        line = raw.strip()
        if not line:
            continue
        if in_comment:
            if "*/" in line:
                in_comment = False
            continue
        if line.startswith("/*"):
            if "*/" not in line:
                in_comment = True
            continue
        if line.startswith("@import"):
            continue
        if len(line) >= 6:
            return line
    return None
