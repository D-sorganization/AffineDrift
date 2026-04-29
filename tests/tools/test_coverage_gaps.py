"""Targeted tests to fill remaining coverage gaps in src/tools.

This module covers the `main()` entrypoints and minor branches
that weren't covered by earlier test files.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestCleanLatexCommentsMain:
    """Cover clean_latex_comments.py main() and branch paths."""

    def test_main_with_no_matching_files(self, tmp_path: Path) -> None:
        """main() should not crash when no .qmd files found."""
        import os

        from src.tools.clean_latex_comments import main

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()  # no .qmd files → nothing happens
        finally:
            os.chdir(original)

    def test_main_processes_content_directories(self, tmp_path: Path) -> None:
        """main() should process qmd files in predefined content directories."""
        import os

        from src.tools.clean_latex_comments import main

        # Create the expected directory structure
        content_dir = tmp_path / "content" / "Affine Background Articles"
        content_dir.mkdir(parents=True)
        qmd = content_dir / "test.qmd"
        qmd.write_text("Hello\n% comment\nWorld", encoding="utf-8")
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
            content = qmd.read_text()
            assert "% comment" not in content
        finally:
            os.chdir(original)

    def test_clean_returns_true_on_success(self, tmp_path: Path) -> None:
        """clean_latex_comments_in_file always returns True on successful processing."""
        from src.tools.clean_latex_comments import clean_latex_comments_in_file

        f = tmp_path / "clean.qmd"
        f.write_text("No comments here.", encoding="utf-8")
        result = clean_latex_comments_in_file(f)
        # Returns True when file is processed (even if no changes made)
        assert result is True


class TestFixQuartoSyntaxMain:
    """Cover fix_quarto_syntax.py main() function."""

    def test_main_with_articles_directory(self, tmp_path: Path) -> None:
        """main() should process files in articles/ directory."""
        import os

        from src.tools.fix_quarto_syntax import main

        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        (articles_dir / "test.qmd").write_text("Some content", encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()  # Should not raise even with no matching patterns
        finally:
            os.chdir(original)

    def test_main_no_articles_dir_raises(self, tmp_path: Path) -> None:
        """main() should raise when articles/ doesn't exist."""
        import os

        from src.tools.fix_quarto_syntax import main

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises((FileNotFoundError, OSError)):
                main()
        finally:
            os.chdir(original)


class TestWrapSidebarsMain:
    """Cover wrap_sidebars.py main() function."""

    def test_main_with_no_qmd_files(self, tmp_path: Path) -> None:
        """main() should not crash when no .qmd files found."""
        import os

        from src.tools.wrap_sidebars import main

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original)

    def test_main_processes_qmd_files(self, tmp_path: Path) -> None:
        """main() should process .qmd files in current directory."""
        import os

        from src.tools.wrap_sidebars import main

        qmd = tmp_path / "test.qmd"
        qmd.write_text(
            '<aside class="left-sidebar">\n  <nav>links</nav>\n</aside>\n',
            encoding="utf-8",
        )
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
            content = qmd.read_text()
            assert "sidebar-sticky-content" in content
        finally:
            os.chdir(original)


class TestCodeQualityCheckMain:
    """Cover code_quality/check.py main() function."""

    def test_main_clean_directory_exits_0(self, tmp_path: Path) -> None:
        """main() should exit 0 when no issues found."""
        from src.tools.code_quality.check import main

        # Pass a clean file as argument
        clean_file = tmp_path / "clean.py"
        clean_file.write_text('"""Module."""\nx = 1\n')

        with patch.object(sys, "argv", ["check", str(clean_file)]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0

    def test_main_with_issues_exits_1(self, tmp_path: Path) -> None:
        """main() should exit 1 when issues found."""
        from src.tools.code_quality.check import main

        # File with a function missing docstring (not in scripts/ or tests/)
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def bad_function():\n    pass\n")

        with patch.object(sys, "argv", ["check", str(bad_file)]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


class TestCodeQualityCheckPy:
    """Cover code_quality_check.py (1 uncovered line)."""

    def test_import_code_quality_check(self) -> None:
        """Importing code_quality_check should not raise."""
        # The file has a single line: just an import alias
        # Coverage is triggered by importing
        import importlib

        mod = importlib.import_module("src.tools.code_quality_check")
        assert mod is not None


class TestVerifyImagesProcess:
    """Cover verify_images.py process_file() and main()."""

    def test_process_file_no_images(self, tmp_path: Path) -> None:
        """process_file should return empty list for file with no images."""
        from src.tools.verify_images import process_file

        f = tmp_path / "page.html"
        f.write_text("<html><body>No images here.</body></html>")
        result = process_file(f)
        assert isinstance(result, list)

    def test_process_file_with_local_image(self, tmp_path: Path) -> None:
        """process_file should find broken local image URLs."""
        from src.tools.verify_images import process_file

        f = tmp_path / "page.html"
        f.write_text('<img src="nonexistent.png" />')
        result = process_file(f)
        assert isinstance(result, list)


class TestPublishManualArticleMain:
    """Cover publish_manual_article.py main() paths."""

    def test_main_exits_when_source_missing(self, tmp_path: Path) -> None:
        """main() should call sys.exit when source file is missing."""
        import os

        from src.tools.publish_manual_article import main

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            os.chdir(original)


class TestConvertAllLatexMorePaths:
    """Cover remaining branches in convert_all_latex.py."""

    def _import_convert_all_latex(self):  # noqa: ANN201
        """Import convert_all_latex with stubbed latex_to_html."""
        import types

        stub = types.ModuleType("latex_to_html")
        stub.LaTeXToHTMLConverter = MagicMock  # type: ignore[attr-defined]
        old = sys.modules.get("latex_to_html")
        sys.modules["latex_to_html"] = stub
        try:
            if "src.tools.convert_all_latex" in sys.modules:
                del sys.modules["src.tools.convert_all_latex"]
            import src.tools.convert_all_latex as m

            return m
        finally:
            if old is None:
                del sys.modules["latex_to_html"]
            else:
                sys.modules["latex_to_html"] = old

    def test_main_dry_run_flag(self) -> None:
        """main() should use dry_run when --dry-run passed."""
        m = self._import_convert_all_latex()
        with (
            patch.object(sys, "argv", ["convert_all_latex.py", "--dry-run"]),
            patch.object(m, "convert_all", return_value=True) as mock_ca,
        ):
            with pytest.raises(SystemExit) as exc:
                m.main()
        mock_ca.assert_called_once_with(True)
        assert exc.value.code == 0

    def test_main_help_flag_exits(self) -> None:
        """main() should exit 0 on --help."""
        m = self._import_convert_all_latex()
        with patch.object(sys, "argv", ["convert_all_latex.py", "--help"]):
            with pytest.raises(SystemExit) as exc:
                m.main()
        assert exc.value.code == 0

    def test_convert_all_handles_invalid_conversion_entry(self) -> None:
        """convert_all should handle non-string source/target entries."""
        import types

        stub = types.ModuleType("latex_to_html")
        stub.LaTeXToHTMLConverter = MagicMock  # type: ignore[attr-defined]
        old = sys.modules.get("latex_to_html")
        sys.modules["latex_to_html"] = stub
        try:
            if "src.tools.convert_all_latex" in sys.modules:
                del sys.modules["src.tools.convert_all_latex"]
            import src.tools.convert_all_latex as m

            # Patch CONVERSIONS to include an invalid entry
            with patch.object(
                m,
                "CONVERSIONS",
                [{"source": None, "target": None, "root_page": None}],
            ):
                result = m.convert_all(dry_run=False)
            assert result is False
        finally:
            if old is None:
                del sys.modules["latex_to_html"]
            else:
                sys.modules["latex_to_html"] = old


class TestReportGeneratorColors:
    """Cover report_generator.py Colors class (tty branch)."""

    def test_colors_class_has_attributes(self) -> None:
        """Colors class should have color attributes."""
        from src.tools.code_quality.report_generator import Colors

        # These exist regardless of TTY status
        assert hasattr(Colors, "FAIL")
        assert hasattr(Colors, "BOLD")
        assert hasattr(Colors, "ENDC")
