"""Tests for scripts/check_upstreamdrift_install_docs.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_upstreamdrift_install_docs import check_file, main


def test_check_file_flags_missing_substring(tmp_path: Path) -> None:
    sample = tmp_path / "sample.qmd"
    sample.write_text("pip install -e .\n", encoding="utf-8")
    errors = check_file(
        sample,
        required=("git submodule update --init --recursive vendor/ud-tools",),
        forbidden=(),
    )
    assert any("missing required" in err for err in errors)


def test_check_file_flags_forbidden_lfs_claim(tmp_path: Path) -> None:
    sample = tmp_path / "sample.qmd"
    sample.write_text("Git LFS is required\n", encoding="utf-8")
    errors = check_file(sample, required=(), forbidden=("Git LFS is required",))
    assert errors


def test_main_passes_on_repo_contract_files() -> None:
    assert main([]) == 0
