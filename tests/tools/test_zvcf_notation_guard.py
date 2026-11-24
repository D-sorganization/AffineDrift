"""Unit tests for zvcf_notation_guard helpers."""

from __future__ import annotations

from pathlib import Path

from src.tools.zvcf_notation_guard import scan_legacy_zvcf_definitions


def test_detects_holding_torque_wording(tmp_path: Path) -> None:
    sample = tmp_path / "pages" / "sample.qmd"
    sample.parent.mkdir(parents=True)
    sample.write_text(
        "ZVCF asks what torque would be needed just to hold a position still.\n",
        encoding="utf-8",
    )
    findings = scan_legacy_zvcf_definitions(tmp_path)
    assert findings and findings[0]["pattern"] == "legacy holding-torque ZVCF summary"
