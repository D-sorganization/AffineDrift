"""Tests for shared batch conversion helpers."""

from __future__ import annotations

import logging
from pathlib import Path

from src.tools.conversion_batch import run_batch_conversion


class RecordingConverter:
    """File converter test double that records conversion calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def convert_file(self, source: str, target: str) -> None:
        """Record a conversion request."""
        self.calls.append((source, target))


def test_run_batch_conversion_converts_existing_files(tmp_path: Path) -> None:
    """Existing sources are converted and counted as successful."""
    source = tmp_path / "input.tex"
    source.write_text("content", encoding="utf-8")
    target = tmp_path / "output.qmd"
    converter = RecordingConverter()

    successes, errors = run_batch_conversion(
        conversions=[{"source": str(source), "target": str(target)}],
        converter=converter,
        logger=logging.getLogger("test-conversion"),
        dry_run=False,
    )

    assert (successes, errors) == (1, 0)
    assert converter.calls == [(str(source), str(target))]


def test_run_batch_conversion_reports_invalid_and_missing_entries(tmp_path: Path, caplog) -> None:
    """Invalid mappings and missing sources are counted as errors."""
    converter = RecordingConverter()

    with caplog.at_level(logging.WARNING):
        successes, errors = run_batch_conversion(
            conversions=[
                {"source": tmp_path / "not-a-string", "target": "out.qmd"},
                {
                    "source": str(tmp_path / "missing.tex"),
                    "target": "out.qmd",
                    "title": "Missing Source",
                },
            ],
            converter=converter,
            logger=logging.getLogger("test-conversion"),
            dry_run=False,
            description_key="title",
        )

    assert (successes, errors) == (0, 2)
    assert converter.calls == []
    assert "Source file not found" in caplog.text


def test_run_batch_conversion_dry_run_does_not_call_converter(tmp_path: Path) -> None:
    """Dry-runs validate source existence without writing targets."""
    source = tmp_path / "input.tex"
    source.write_text("content", encoding="utf-8")
    converter = RecordingConverter()

    successes, errors = run_batch_conversion(
        conversions=[{"source": str(source), "target": str(tmp_path / "out.qmd")}],
        converter=converter,
        logger=logging.getLogger("test-conversion"),
        dry_run=True,
    )

    assert (successes, errors) == (1, 0)
    assert converter.calls == []
