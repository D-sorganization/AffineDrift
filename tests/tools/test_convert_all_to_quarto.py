"""Tests for src.tools.convert_all_to_quarto — batch LaTeX to Quarto converter."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _import_convert_all_to_quarto():  # noqa: ANN201
    """Import convert_all_to_quarto through package-qualified imports."""
    if "src.tools.convert_all_to_quarto" in sys.modules:
        del sys.modules["src.tools.convert_all_to_quarto"]
    import src.tools.convert_all_to_quarto as m

    return m


class TestSetupArticlesDirectory:
    """Tests for setup_articles_directory()."""

    def test_creates_articles_directory(self, tmp_path: Path) -> None:
        """Should create the articles directory if it doesn't exist."""
        import os

        m = _import_convert_all_to_quarto()
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            original_articles = m.ARTICLES_DIR
            m.ARTICLES_DIR = str(tmp_path / "articles")
            m.setup_articles_directory()
            assert (tmp_path / "articles").exists()
        finally:
            m.ARTICLES_DIR = original_articles
            os.chdir(original)

    def test_creates_metadata_file(self, tmp_path: Path) -> None:
        """Should create _metadata.yml in articles directory."""
        import os

        m = _import_convert_all_to_quarto()
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            original_articles = m.ARTICLES_DIR
            articles = str(tmp_path / "articles")
            m.ARTICLES_DIR = articles
            m.setup_articles_directory()
            metadata = tmp_path / "articles" / "_metadata.yml"
            assert metadata.exists()
        finally:
            m.ARTICLES_DIR = original_articles
            os.chdir(original)

    def test_does_not_overwrite_existing_metadata(self, tmp_path: Path) -> None:
        """Should not overwrite existing _metadata.yml."""
        import os

        m = _import_convert_all_to_quarto()
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            original_articles = m.ARTICLES_DIR
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            metadata = articles_dir / "_metadata.yml"
            metadata.write_text("existing: true", encoding="utf-8")
            m.ARTICLES_DIR = str(articles_dir)
            m.setup_articles_directory()
            assert metadata.read_text() == "existing: true"
        finally:
            m.ARTICLES_DIR = original_articles
            os.chdir(original)


class TestConvertAll:
    """Tests for convert_all()."""

    def test_dry_run_mode(self) -> None:
        """convert_all(dry_run=True) should not convert files."""
        m = _import_convert_all_to_quarto()
        with patch.object(m, "CONVERSIONS", []):
            result = m.convert_all(True)
        assert result is True

    def test_returns_false_when_source_missing(self) -> None:
        """convert_all should return False when source files are missing."""
        m = _import_convert_all_to_quarto()
        with patch.object(
            m,
            "CONVERSIONS",
            [{"source": "/nonexistent/file.tex", "target": "out.qmd", "description": "test"}],
        ):
            result = m.convert_all(False)
        assert result is False

    def test_convert_file_called_when_source_exists(self, tmp_path: Path) -> None:
        """convert_all should call convert_file when source exists."""
        m = _import_convert_all_to_quarto()

        source = tmp_path / "source.tex"
        source.write_text(r"\begin{document}content\end{document}", encoding="utf-8")
        target = str(tmp_path / "output.qmd")

        mock_converter = MagicMock()
        m.LaTeXToQuartoConverter = MagicMock(return_value=mock_converter)

        with patch.object(
            m,
            "CONVERSIONS",
            [{"source": str(source), "target": target, "description": "test"}],
        ):
            with patch.object(m, "setup_articles_directory"):
                m.convert_all(False)
        mock_converter.convert_file.assert_called_once()


class TestMain:
    """Tests for main()."""

    def test_main_help_exits_0(self) -> None:
        """main() should exit 0 on --help."""
        m = _import_convert_all_to_quarto()
        with patch.object(sys, "argv", ["convert_all_to_quarto.py", "--help"]):
            with pytest.raises(SystemExit) as exc:
                m.main()
        assert exc.value.code == 0

    def test_main_dry_run_exits_0_when_no_sources(self) -> None:
        """main() with --dry-run and empty CONVERSIONS should exit 0."""
        m = _import_convert_all_to_quarto()
        with (
            patch.object(sys, "argv", ["convert_all_to_quarto.py", "--dry-run"]),
            patch.object(m, "CONVERSIONS", []),
        ):
            with pytest.raises(SystemExit) as exc:
                m.main()
        assert exc.value.code == 0
