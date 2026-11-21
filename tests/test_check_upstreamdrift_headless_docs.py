"""Tests for scripts/check_upstreamdrift_headless_docs.py (#5626)."""

from __future__ import annotations

from pathlib import Path

from scripts.check_upstreamdrift_headless_docs import check_file, main


def test_check_file_flags_missing_ud_sim(tmp_path: Path) -> None:
    sample = tmp_path / "sample.qmd"
    sample.write_text("REST only\n", encoding="utf-8")
    errors = check_file(
        sample,
        required=("ud-sim",),
        forbidden=(),
    )
    assert any("missing required" in err for err in errors)


def test_main_passes_on_repo_contract_files() -> None:
    assert main([]) == 0
