"""Tests for src.tools.utils.conversion_utils.batch_convert."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from src.tools.utils.conversion_utils import batch_convert


@pytest.fixture()
def mock_logger() -> logging.Logger:
    """Return a MagicMock that passes isinstance(x, logging.Logger) checks."""
    return MagicMock(spec=logging.Logger)


class TestBatchConvertDryRun:
    """Tests for batch_convert in dry_run=True mode."""

    def test_dry_run_empty_list_returns_true(self, mock_logger: logging.Logger) -> None:
        """Empty file_pairs with dry_run should return True (no errors)."""
        converter = MagicMock()
        result = batch_convert(converter, [], dry_run=True, logger=mock_logger)
        assert result is True
        converter.convert_file.assert_not_called()

    def test_dry_run_with_existing_source_does_not_convert(
        self, mock_logger: logging.Logger, tmp_path
    ) -> None:
        """dry_run=True should not call convert_file even when source exists."""
        source = tmp_path / "input.tex"
        source.write_text(r"\begin{document}\end{document}", encoding="utf-8")
        target = str(tmp_path / "output.html")
        converter = MagicMock()

        result = batch_convert(
            converter,
            [{"source": str(source), "target": target}],
            dry_run=True,
            logger=mock_logger,
        )

        assert result is True
        converter.convert_file.assert_not_called()
        mock_logger.info.assert_called()

    def test_dry_run_with_missing_source_returns_false(self, mock_logger: logging.Logger) -> None:
        """dry_run=True with a missing source file should return False."""
        converter = MagicMock()
        result = batch_convert(
            converter,
            [{"source": "/nonexistent/file.tex", "target": "out.html"}],
            dry_run=True,
            logger=mock_logger,
        )
        assert result is False
        mock_logger.warning.assert_called_once()
        converter.convert_file.assert_not_called()


class TestBatchConvertLive:
    """Tests for batch_convert in dry_run=False (live) mode."""

    def test_live_conversion_success(self, mock_logger: logging.Logger, tmp_path) -> None:
        """Successful convert_file call should return True."""
        source = tmp_path / "input.tex"
        source.write_text(r"\begin{document}\end{document}", encoding="utf-8")
        target = str(tmp_path / "output.html")
        converter = MagicMock()

        result = batch_convert(
            converter,
            [{"source": str(source), "target": target}],
            dry_run=False,
            logger=mock_logger,
        )

        assert result is True
        converter.convert_file.assert_called_once_with(str(source), target)

    def test_live_conversion_oserror_returns_false(
        self, mock_logger: logging.Logger, tmp_path
    ) -> None:
        """OSError from convert_file should cause return False."""
        source = tmp_path / "input.tex"
        source.write_text(r"\begin{document}\end{document}", encoding="utf-8")
        converter = MagicMock()
        converter.convert_file.side_effect = OSError("disk error")

        result = batch_convert(
            converter,
            [{"source": str(source), "target": "out.html"}],
            dry_run=False,
            logger=mock_logger,
        )

        assert result is False
        mock_logger.error.assert_called()

    def test_live_conversion_value_error_returns_false(
        self, mock_logger: logging.Logger, tmp_path
    ) -> None:
        """ValueError from convert_file should cause return False."""
        source = tmp_path / "input.tex"
        source.write_text("data", encoding="utf-8")
        converter = MagicMock()
        converter.convert_file.side_effect = ValueError("bad input")

        result = batch_convert(
            converter,
            [{"source": str(source), "target": "out.html"}],
            dry_run=False,
            logger=mock_logger,
        )

        assert result is False

    def test_missing_source_returns_false(self, mock_logger: logging.Logger) -> None:
        """Missing source file in live mode should return False."""
        converter = MagicMock()
        result = batch_convert(
            converter,
            [{"source": "/nonexistent/file.tex", "target": "out.html"}],
            dry_run=False,
            logger=mock_logger,
        )
        assert result is False
        converter.convert_file.assert_not_called()

    def test_partial_failure_returns_false(self, mock_logger: logging.Logger, tmp_path) -> None:
        """One missing + one success should return False overall."""
        good_source = tmp_path / "good.tex"
        good_source.write_text("data", encoding="utf-8")
        converter = MagicMock()

        file_pairs = [
            {"source": "/nonexistent/bad.tex", "target": "bad.html"},
            {"source": str(good_source), "target": "good.html"},
        ]
        result = batch_convert(converter, file_pairs, dry_run=False, logger=mock_logger)
        assert result is False
        # good source still gets converted
        converter.convert_file.assert_called_once()


class TestBatchConvertValidation:
    """Tests for DbC validation in batch_convert."""

    def test_non_string_source_returns_false(self, mock_logger: logging.Logger) -> None:
        """Entry with non-string source should return False."""
        converter = MagicMock()
        result = batch_convert(
            converter,
            [{"source": 123, "target": "out.html"}],
            dry_run=False,
            logger=mock_logger,
        )
        assert result is False
        mock_logger.error.assert_called()

    def test_non_string_target_returns_false(self, mock_logger: logging.Logger) -> None:
        """Entry with non-string target should return False."""
        converter = MagicMock()
        result = batch_convert(
            converter,
            [{"source": "file.tex", "target": None}],
            dry_run=False,
            logger=mock_logger,
        )
        assert result is False

    def test_empty_list_live_returns_true(self, mock_logger: logging.Logger) -> None:
        """Empty file_pairs in live mode returns True (no errors)."""
        converter = MagicMock()
        result = batch_convert(converter, [], dry_run=False, logger=mock_logger)
        assert result is True
