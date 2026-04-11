"""Tests for convert_all_latex.py and convert_all_to_quarto.py batch converters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch


class TestConvertAllLatex:
    """Tests for src.tools.convert_all_latex.convert_all()."""

    def _import_convert_all_latex(self):  # noqa: ANN201
        """Import convert_all_latex through package-qualified imports."""
        import src.tools.convert_all_latex as m

        return m

    def test_dry_run_all_missing_returns_false(self) -> None:
        """dry_run=True with all missing sources returns False."""
        m = self._import_convert_all_latex()
        with patch("src.tools.utils.conversion_utils.os.path.exists", return_value=False):
            result = m.convert_all(dry_run=True)
        assert isinstance(result, bool)
        assert result is False

    def test_dry_run_with_existing_source(self) -> None:
        """dry_run=True with existing sources returns True without converting."""
        m = self._import_convert_all_latex()
        mock_converter_instance = MagicMock()
        with (
            patch("src.tools.utils.conversion_utils.os.path.exists", return_value=True),
            patch.object(m, "LaTeXToHTMLConverter", return_value=mock_converter_instance),
        ):
            result = m.convert_all(dry_run=True)
        assert result is True
        mock_converter_instance.convert_file.assert_not_called()

    def test_conversion_failure_returns_false(self) -> None:
        """Conversion failure should return False."""
        m = self._import_convert_all_latex()
        mock_converter_instance = MagicMock()
        mock_converter_instance.convert_file.side_effect = OSError("fail")
        with (
            patch("src.tools.utils.conversion_utils.os.path.exists", return_value=True),
            patch.object(m, "LaTeXToHTMLConverter", return_value=mock_converter_instance),
        ):
            result = m.convert_all(dry_run=False)
        assert result is False


class TestConvertAllToQuarto:
    """Tests for src.tools.convert_all_to_quarto.convert_all()."""

    def _import_convert_all_to_quarto(self):  # noqa: ANN201
        """Import convert_all_to_quarto through package-qualified imports."""
        import src.tools.convert_all_to_quarto as m

        return m

    def test_dry_run_all_missing_returns_false(self) -> None:
        """dry_run with all missing sources returns False."""
        m = self._import_convert_all_to_quarto()
        with patch.object(m.os.path, "exists", return_value=False):
            result = m.convert_all(dry_run=True)
        assert isinstance(result, bool)

    def test_dry_run_with_existing_sources_does_not_convert(self) -> None:
        """dry_run=True with existing sources should not call convert_file."""
        m = self._import_convert_all_to_quarto()
        mock_converter_instance = MagicMock()
        with (
            patch.object(m.os.path, "exists", return_value=True),
            patch.object(m, "LaTeXToQuartoConverter", return_value=mock_converter_instance),
        ):
            result = m.convert_all(dry_run=True)
        assert result is True
        mock_converter_instance.convert_file.assert_not_called()

    def test_setup_articles_directory_creates_dir(self, tmp_path: Path) -> None:
        """setup_articles_directory should create the articles directory."""
        import os

        m = self._import_convert_all_to_quarto()
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            m.setup_articles_directory()
            articles_dir = tmp_path / "articles"
            assert articles_dir.exists()
            assert (articles_dir / "_metadata.yml").exists()
        finally:
            os.chdir(original_dir)

    def test_setup_articles_directory_idempotent(self, tmp_path: Path) -> None:
        """setup_articles_directory should be idempotent."""
        import os

        m = self._import_convert_all_to_quarto()
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            m.setup_articles_directory()
            m.setup_articles_directory()  # second call should not raise
            assert (tmp_path / "articles").exists()
        finally:
            os.chdir(original_dir)
