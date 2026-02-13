"""Tests for CLI contract helpers."""

import pytest

from src.tools.utils.cli_contracts import parse_csv_enum


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
