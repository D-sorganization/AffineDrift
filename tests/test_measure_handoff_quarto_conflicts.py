"""Unit tests for scripts/measure_handoff_quarto_conflicts.py (issue #5250)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.measure_handoff_quarto_conflicts import (
    ConflictMeasurement,
    compute_counts_from_timestamps,
    load_git_window_counts,
    main,
    measure_default_60d_window,
    render_markdown_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rerun_yields_identical_reproducible_counts(tmp_path: Path) -> None:
    """Rerunning the query script yields the exact same deterministic counts."""
    first: ConflictMeasurement = measure_default_60d_window()
    second: ConflictMeasurement = measure_default_60d_window()

    assert first == second
    assert first.window_start == "2026-08-30"
    assert first.window_end == "2026-10-29"
    assert first.handoff_commits_60d == 253
    assert first.handoff_commits_post_rm5 == 10
    assert first.quarto_commits_60d == 34
    assert first.quarto_commits_post_rm5 == 10
    assert first.recommendation == "NO-GO"

    out1 = tmp_path / "run1.md"
    out2 = tmp_path / "run2.md"
    assert main(["--output", str(out1)]) == 0
    assert main(["--output", str(out2)]) == 0
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


def test_compute_counts_from_timestamps_and_boundary_validation(tmp_path: Path) -> None:
    """Timestamp partitioning and git boundary validation behave deterministically."""
    counts = compute_counts_from_timestamps(
        ["2026-09-10T10:00:00Z", "2026-10-01T12:00:00Z", "2026-10-24T09:53:51Z"],
        ["2026-09-30T08:00:00Z", "2026-10-25T02:06:04Z"],
        rm5_cutoff="2026-10-05T01:35:07Z",
    )
    assert counts == {
        "handoff_60d": 3,
        "handoff_pre_rm5": 2,
        "handoff_post_rm5": 1,
        "quarto_60d": 2,
        "quarto_pre_rm5": 1,
        "quarto_post_rm5": 1,
    }

    with pytest.raises(ValueError, match="Not a git repository"):
        load_git_window_counts(tmp_path / "not-a-repo")


def test_committed_report_matches_rendered_measurement() -> None:
    """Committed audit report includes #5105 vs #5107/#5141 analysis and NO-GO recommendation."""
    measurement = measure_default_60d_window()
    rendered = render_markdown_report(measurement)
    committed = (
        REPO_ROOT / "docs" / "audits" / "handoff-quarto-conflict-frequency-5250.md"
    ).read_text(encoding="utf-8")
    assert rendered == committed
    assert "#5105" in committed
    assert "#5107" in committed
    assert "#5141" in committed
    assert "NO-GO" in committed
