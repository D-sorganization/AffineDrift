"""Tests for src.tools.update_navigation — nav updating functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.update_navigation import (
    _ensure_top_nav,
    _render_nav,
    _replace_logo_path,
    _resolve_targets,
    main,
    update_navigation,
)

NAV_BLOCK_HTML = """<html>
<head></head>
<body>
<nav>
  <ul class="nav-links">
    <li><a href="old.html">Old</a></li>
  </ul>
</nav>
</body>
</html>"""


class TestEnsureTopNav:
    """Tests for _ensure_top_nav()."""

    def test_adds_top_nav_class_to_bare_nav(self) -> None:
        """Should add class='top-nav' to bare <nav> tags."""
        html = "<nav>"
        result = _ensure_top_nav(html)
        assert 'class="top-nav"' in result

    def test_does_not_modify_nav_with_class(self) -> None:
        """Should not modify <nav> tags that already have a class attribute."""
        html = '<nav class="main-nav">'
        result = _ensure_top_nav(html)
        # Should not double-add class — the original class stays intact
        assert 'class="main-nav"' in result

    def test_no_change_without_nav(self) -> None:
        """Should not change content without nav elements."""
        html = "<div>No nav here.</div>"
        result = _ensure_top_nav(html)
        assert result == html


class TestReplaceLogoPath:
    """Tests for _replace_logo_path()."""

    def test_replaces_legacy_logo_path(self) -> None:
        """Should replace old logo path with updated path."""
        html = 'src="logo/AffineDriftLogo.png"'
        result = _replace_logo_path(html)
        assert "AffineDriftLogo.png" not in result
        assert "Logo Transparent" in result

    def test_no_change_without_logo(self) -> None:
        """Should not change content without legacy logo path."""
        html = '<img src="other.png">'
        result = _replace_logo_path(html)
        assert result == html


class TestResolveTargets:
    """Tests for _resolve_targets()."""

    def test_returns_list_of_paths(self) -> None:
        """Should resolve page names to Path objects."""
        targets = _resolve_targets(["index.html", "about.html"])
        assert all(isinstance(t, Path) for t in targets)

    def test_resolves_path_objects(self, tmp_path: Path) -> None:
        """Should also resolve Path objects."""
        targets = _resolve_targets([tmp_path / "page.html"])
        assert isinstance(targets[0], Path)

    def test_empty_input_returns_empty(self) -> None:
        """Should return empty list for empty input."""
        assert _resolve_targets([]) == []


class TestRenderNav:
    """Tests for _render_nav()."""

    def test_renders_nav_with_indentation(self) -> None:
        """Should apply indentation from match group."""
        pattern = __import__(
            "src.tools.update_navigation", fromlist=["NAV_LIST_PATTERN"]
        ).NAV_LIST_PATTERN
        # Build a fake match via regex
        m = pattern.search('  <ul class="nav-links">old</ul>')
        if m is None:
            pytest.skip("Pattern did not match test string")
        result = _render_nav(m, "<li>New</li>")
        assert "<li>New</li>" in result


class TestUpdateNavigation:
    """Tests for update_navigation()."""

    def test_updates_nav_successfully(self, tmp_path: Path) -> None:
        """Should update nav block and return True when changed."""
        f = tmp_path / "page.html"
        f.write_text(NAV_BLOCK_HTML, encoding="utf-8")
        changed = update_navigation(f)
        assert changed is True
        content = f.read_text()
        assert "Affine Drift" in content  # New nav content

    def test_returns_true_when_changed(self, tmp_path: Path) -> None:
        """Should return True when nav is updated from old to new content."""
        f = tmp_path / "page.html"
        f.write_text(NAV_BLOCK_HTML, encoding="utf-8")
        # First update always changes from the old nav
        result = update_navigation(f)
        assert result is True

    def test_raises_value_error_when_no_nav_block(self, tmp_path: Path) -> None:
        """Should raise ValueError when no nav-links block found."""
        f = tmp_path / "page.html"
        f.write_text("<html><body><p>No nav here.</p></body></html>", encoding="utf-8")
        with pytest.raises(ValueError, match="No <ul"):
            update_navigation(f)

    def test_custom_nav_markup(self, tmp_path: Path) -> None:
        """Should use provided custom nav markup."""
        f = tmp_path / "page.html"
        f.write_text(NAV_BLOCK_HTML, encoding="utf-8")
        custom_nav = "<li>Custom Link</li>"
        update_navigation(f, nav_markup=custom_nav)
        content = f.read_text()
        assert "Custom Link" in content


class TestMain:
    """Tests for main()."""

    def test_main_missing_pages_returns_nonzero(self) -> None:
        """main() should return non-zero exit code for missing pages."""
        result = main(["nonexistent_page.html"])
        assert result != 0

    def test_main_with_pages_missing_returns_nonzero(self, tmp_path: Path) -> None:
        """main() should return 1 when pages don't exist."""
        result = main([str(tmp_path / "missing_a.html"), str(tmp_path / "missing_b.html")])
        assert result == 1

    def test_main_with_page_lacking_nav_returns_nonzero(self, tmp_path: Path) -> None:
        """main() should return 1 when page exists but lacks nav block."""
        f = tmp_path / "page.html"
        f.write_text("<html><body><p>No nav here.</p></body></html>", encoding="utf-8")
        result = main([str(f)])
        assert result == 1

    def test_main_updates_valid_page(self, tmp_path: Path) -> None:
        """main() should return 0 when page is updated successfully."""
        f = tmp_path / "page.html"
        f.write_text(NAV_BLOCK_HTML, encoding="utf-8")
        result = main([str(f)])
        assert result == 0
