"""Tests for series architecture and progress tracking documentation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH_DOC = ROOT / "docs" / "development" / "geometry_of_motion_architecture.md"


def test_architecture_tracking_doc_exists() -> None:
    """Master architecture tracking document should exist in docs/development."""
    assert ARCH_DOC.exists()


def test_architecture_tracking_doc_links_open_series_issues() -> None:
    """Architecture doc should track active issue IDs for the series."""
    text = ARCH_DOC.read_text(encoding="utf-8")
    assert "#1267" in text
    assert "#1268" in text
    assert "#1269" in text
    assert "#1274" in text
    assert "#1290" in text
