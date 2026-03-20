"""Tests for wrap_sidebars.py — sidebar sticky div wrapping."""

from pathlib import Path

from src.tools.wrap_sidebars import wrap_file


class TestWrapFile:
    """Tests for wrap_file()."""

    def test_wraps_left_sidebar(self, tmp_path: Path) -> None:
        """Should wrap left-sidebar content in sticky div."""
        content = '<aside class="left-sidebar">\n  <nav>links</nav>\n</aside>\n'
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        assert "sidebar-sticky-content" in result

    def test_wraps_right_sidebar(self, tmp_path: Path) -> None:
        """Should wrap right-sidebar content in sticky div."""
        content = '<aside class="right-sidebar">\n  <nav>toc</nav>\n</aside>\n'
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        assert "sidebar-sticky-content" in result

    def test_wraps_resources_sidebar(self, tmp_path: Path) -> None:
        """Should wrap resources-sidebar content in sticky div."""
        content = '<aside class="resources-sidebar">\n  <ul>items</ul>\n</aside>\n'
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        assert "sidebar-sticky-content" in result

    def test_no_modification_when_no_sidebars(self, tmp_path: Path) -> None:
        """Should not modify files without sidebar elements."""
        content = "# Hello\nSome content without sidebars.\n"
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        assert result == content

    def test_skips_already_wrapped_left_sidebar(self, tmp_path: Path) -> None:
        """Should not double-wrap already-wrapped left sidebar."""
        content = (
            '<aside class="left-sidebar">\n'
            '        <div class="sidebar-sticky-content">\n'
            "          <nav>links</nav>\n"
            "        </div>\n"
            "      </aside>\n"
        )
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        # Should not have double-wrapped
        assert result.count("sidebar-sticky-content") == 1

    def test_file_written_on_change(self, tmp_path: Path) -> None:
        """Should write file when content changes."""
        content = '<aside class="left-sidebar">\n  <nav>links</nav>\n</aside>\n'
        qmd_file = tmp_path / "test.qmd"
        qmd_file.write_text(content)
        wrap_file(qmd_file)
        result = qmd_file.read_text()
        assert result != content
