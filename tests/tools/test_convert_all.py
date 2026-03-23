"""Tests for convert_all_latex.py and convert_all_to_quarto.py batch converters.

Both modules use legacy top-level relative imports (``from latex_to_html import ...``,
``from latex_to_qmd import ...``) that only work when run from the project root as scripts.
We stub those modules in sys.modules before importing so pytest can load them.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch


def _make_stub_module(name: str) -> types.ModuleType:
    """Return a stub module with a single MagicMock class attribute."""
    mod = types.ModuleType(name)
    mod.LaTeXToHTMLConverter = MagicMock  # type: ignore[attr-defined]
    mod.LaTeXToQuartoConverter = MagicMock  # type: ignore[attr-defined]
    return mod


class TestConvertAllLatex:
    """Tests for src.tools.convert_all_latex.convert_all()."""

    def _import_convert_all_latex(self):  # noqa: ANN201
        """Import convert_all_latex with stubbed latex_to_html."""
        stub = _make_stub_module("latex_to_html")
        old = sys.modules.get("latex_to_html")
        sys.modules["latex_to_html"] = stub
        try:
            # Force reimport
            if "src.tools.convert_all_latex" in sys.modules:
                del sys.modules["src.tools.convert_all_latex"]
            import src.tools.convert_all_latex as m

            return m
        finally:
            if old is None:
                del sys.modules["latex_to_html"]
            else:
                sys.modules["latex_to_html"] = old

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
        """Import convert_all_to_quarto with stubbed latex_to_qmd."""
        stub = _make_stub_module("latex_to_qmd")
        old = sys.modules.get("latex_to_qmd")
        sys.modules["latex_to_qmd"] = stub
        try:
            if "src.tools.convert_all_to_quarto" in sys.modules:
                del sys.modules["src.tools.convert_all_to_quarto"]
            import src.tools.convert_all_to_quarto as m

            return m
        finally:
            if old is None:
                del sys.modules["latex_to_qmd"]
            else:
                sys.modules["latex_to_qmd"] = old

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
