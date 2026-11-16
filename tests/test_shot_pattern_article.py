"""Tests for shot-pattern article summary builders (#5639)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.shot_pattern_article.summary import (
    bootstrap_se_from_interval,
    build_article_summary,
    club_range_rows,
    load_headline_dataset,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "articles/shot_pattern_analysis/data"
SHOT_PATTERN_ROOT = ROOT / "articles/shot_pattern_analysis"
ARTICLE = ROOT / "articles/shot-pattern-analysis.qmd"


@pytest.mark.unit
def test_bootstrap_se_from_symmetric_interval() -> None:
    se = bootstrap_se_from_interval(-0.001, 0.001)
    assert se == pytest.approx(0.001 / 1.96, rel=1e-9)


@pytest.mark.unit
def test_club_ranges_match_article_driver_draw_minimum() -> None:
    dataset = load_headline_dataset(DATA_DIR)
    rows = club_range_rows(dataset)
    driver = next(row for row in rows if row["club_id"] == "driver")
    assert driver["draw_sg_min"] == pytest.approx(2.6911773453713196e-05, rel=0, abs=1e-12)
    assert driver["draw_sg_max"] == pytest.approx(0.0077976550468906, rel=1e-9)


@pytest.mark.unit
def test_build_article_summary_writes_markdown_with_se_columns() -> None:
    summary = build_article_summary(DATA_DIR)
    assert "Draw MC SE" in summary["markdown_table"]
    assert "+0.00003" in summary["markdown_table"]
    assert len(summary["exclusion_by_cell"]) == 24
    assert "0.04%" in summary["exclusion_markdown"]


@pytest.mark.content_lint
def test_shot_pattern_committed_data_and_pinned_figure_pipeline() -> None:
    """Tables/data are vendored; figure plates rebuild via pinned UpstreamDrift entrypoint."""
    manifest_path = SHOT_PATTERN_ROOT / "source_manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["study"]["figure_render_entrypoint"]
    assert (SHOT_PATTERN_ROOT / "generators/README.md").is_file()
    for name in (
        "headline_paired_sg.csv",
        "delivery_noise_profiles.json",
        "club_parameters.json",
        "strokes_gained_baseline.json",
    ):
        assert (DATA_DIR / name).is_file(), f"missing committed data artifact: {name}"
    qmd = ARTICLE.read_text(encoding="utf-8")
    assert "build_shot_pattern_article_artifacts" in qmd
    assert "source_manifest.json" in qmd
    assert "SGBroadie2012" in qmd or "strokes_gained_baseline.json" in qmd
