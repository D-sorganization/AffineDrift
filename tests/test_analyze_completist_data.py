"""Behavioral tests for ``scripts/analyze_completist_data.py`` pure helpers (#3230).

Covers ``is_excluded`` (exclusion globs, normalization, empty input),
``_parse_grep_line`` (well-formed and malformed grep lines), and
``calculate_metrics`` (impact/coverage/complexity heuristics + boundaries).
"""

from __future__ import annotations

from scripts.analyze_completist_data import (
    _parse_grep_line,
    calculate_metrics,
    is_excluded,
)


def test_is_excluded_empty_path() -> None:
    assert is_excluded("") is True


def test_is_excluded_matches_excluded_prefix() -> None:
    assert is_excluded("docs/index.md") is True
    assert is_excluded(".github/workflows/ci.yml") is True


def test_is_excluded_normalizes_backslashes_and_dot_slash() -> None:
    assert is_excluded(r".\docs\thing.md") is True


def test_is_excluded_allows_source_files() -> None:
    assert is_excluded("src/core/foo.py") is False


def test_parse_grep_line_well_formed() -> None:
    assert _parse_grep_line("src/a.py:42:  # TODO fix it") == (
        "src/a.py",
        "42",
        "# TODO fix it",
    )


def test_parse_grep_line_too_few_parts() -> None:
    assert _parse_grep_line("no colons here") == (None, None, None)


def test_calculate_metrics_high_impact_for_engines() -> None:
    impact, coverage, complexity = calculate_metrics({"file": "engines/sim.py", "type": "Stub"})
    assert impact == 5
    assert complexity == 4


def test_calculate_metrics_tools_path_is_mid_impact() -> None:
    impact, _coverage, _complexity = calculate_metrics(
        {"file": "src/tools/x.py", "type": "TO" + "DO"}
    )
    assert impact == 3


def test_calculate_metrics_default_low_impact() -> None:
    impact, coverage, _complexity = calculate_metrics(
        {"file": "misc/readme_helper.py", "type": "DocGap"}
    )
    assert impact == 1
    assert coverage == 2  # not tests/ nor shared/python


def test_calculate_metrics_tests_path_high_coverage() -> None:
    _impact, coverage, _complexity = calculate_metrics(
        {"file": "tests/test_x.py", "type": "DocGap"}
    )
    assert coverage == 5


def test_calculate_metrics_placeholder_in_frontend_is_high_impact() -> None:
    impact, _coverage, complexity = calculate_metrics(
        {"file": "site/app.js", "type": "Placeholder"}
    )
    assert impact == 5
    assert complexity == 4


def test_calculate_metrics_unknown_type_default_complexity() -> None:
    _impact, _coverage, complexity = calculate_metrics({"file": "src/x.py", "type": "MysteryType"})
    assert complexity == 3
