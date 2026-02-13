"""Tests for CLI contract helpers."""

from pathlib import Path

import pytest

from src.tools.utils.cli_contracts import (
    ensure_existing_dir,
    ensure_existing_file,
    parse_csv_enum,
)


def test_parse_csv_enum_parses_and_normalizes() -> None:
    parsed = parse_csv_enum(
        " broken, orphaned ",
        allowed={"broken", "orphaned"},
        aliases={"all": {"broken", "orphaned"}},
    )
    assert parsed == {"broken", "orphaned"}


def test_parse_csv_enum_expands_alias() -> None:
    parsed = parse_csv_enum(
        "all",
        allowed={"broken", "orphaned"},
        aliases={"all": {"broken", "orphaned"}},
    )
    assert parsed == {"broken", "orphaned"}


def test_parse_csv_enum_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        parse_csv_enum(
            "broken,invalid",
            allowed={"broken", "orphaned"},
            aliases={"all": {"broken", "orphaned"}},
            value_name="--fail-on value",
        )


def test_ensure_existing_file_returns_path_for_existing_file(tmp_path: Path) -> None:
    report = tmp_path / "summary.json"
    report.write_text("{}", encoding="utf-8")

    validated = ensure_existing_file(str(report), value_name="--input")
    assert validated == report


def test_ensure_existing_file_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="must be an existing file"):
        ensure_existing_file(str(missing), value_name="--input")


def test_ensure_existing_dir_returns_path_for_existing_dir(tmp_path: Path) -> None:
    validated = ensure_existing_dir(str(tmp_path), value_name="--docs-dir")
    assert validated == tmp_path


def test_ensure_existing_dir_raises_for_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "missing_dir"
    with pytest.raises(ValueError, match="must be an existing directory"):
        ensure_existing_dir(str(missing), value_name="--docs-dir")
