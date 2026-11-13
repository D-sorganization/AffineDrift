"""Summarize vendored headline cells for the shot-pattern article."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, TypedDict

CLUB_LABELS = {
    "driver": "Driver",
    "seven_iron": "Seven Iron",
    "pitching_wedge": "Pitching Wedge",
}

HEADLINE_CELL_NAMES = tuple(
    f"{club}_lean0_curve{curve}_rotation{sd}_{profile}"
    for club in ("driver", "seven_iron", "pitching_wedge")
    for curve in (1, 2)
    for sd in (1, 2)
    for profile in ("shaft_only", "combined2")
)

BOOTSTRAP_Z = 1.96
HEADLINE_CSV = "headline_paired_sg.csv"


def _row_to_cell(row: dict[str, str]) -> dict[str, Any]:
    """Convert one headline CSV row into the article cell JSON shape."""

    def f(key: str) -> float:
        """Parse a CSV column as float."""
        return float(row[key])

    def i(key: str) -> int:
        """Parse a CSV column as int (via float for scientific notation)."""
        return int(float(row[key]))

    return {
        "cell": row["cell"],
        "club_id": row["club_id"],
        "scoring_status": row["scoring_status"],
        "paired_n": i("paired_n"),
        "paired_benefit_vs_straight": {
            "Draw": {
                "estimate": f("draw_estimate"),
                "lower_95": f("draw_lower_95"),
                "upper_95": f("draw_upper_95"),
            },
            "Fade": {
                "estimate": f("fade_estimate"),
                "lower_95": f("fade_lower_95"),
                "upper_95": f("fade_upper_95"),
            },
        },
        "geometry": {
            "Straight": {"supported_n": i("supported_straight")},
            "Draw": {"supported_n": i("supported_draw")},
            "Fade": {"supported_n": i("supported_fade")},
        },
    }


def load_headline_dataset(data_dir: Path) -> dict[str, Any]:
    """Load headline cells from ``headline_paired_sg.csv`` and optional metadata JSON."""
    csv_path = data_dir / HEADLINE_CSV
    with csv_path.open(encoding="utf-8", newline="") as handle:
        cells = [_row_to_cell(row) for row in csv.DictReader(handle)]
    meta_path = data_dir / "headline_dataset_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    return {
        "schema": "shot-pattern-headline-cells-lean0/1",
        "bootstrap_resamples": meta.get("bootstrap_resamples", 2000),
        "units": meta.get("units"),
        "cells": cells,
    }


class Interval(TypedDict):
    estimate: float
    lower_95: float
    upper_95: float
    bootstrap_se: float


class ClubRangeRow(TypedDict):
    club_id: str
    club_label: str
    draw_sg_min: float
    draw_sg_max: float
    draw_se_min: float
    draw_se_max: float
    fade_sg_min: float
    fade_sg_max: float
    fade_se_min: float
    fade_se_max: float
    condition_count: int


def bootstrap_se_from_interval(lower_95: float, upper_95: float) -> float:
    """Map a percentile bootstrap interval to an equivalent normal SE."""
    if not all(math.isfinite(v) for v in (lower_95, upper_95)):
        raise ValueError("interval bounds must be finite")
    width = upper_95 - lower_95
    if width < 0:
        raise ValueError("upper_95 must be at least lower_95")
    return width / (2.0 * BOOTSTRAP_Z)


def _pattern_interval(cell: dict[str, Any], pattern: str) -> Interval:
    """Return Draw/Fade paired-benefit interval and bootstrap SE for one cell."""
    paired = cell["paired_benefit_vs_straight"][pattern]
    lower = float(paired["lower_95"])
    upper = float(paired["upper_95"])
    return {
        "estimate": float(paired["estimate"]),
        "lower_95": lower,
        "upper_95": upper,
        "bootstrap_se": bootstrap_se_from_interval(lower, upper),
    }


def _lean0_cells(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the 24 zero-lean headline cells in canonical generation order."""
    by_name = {cell["cell"]: cell for cell in dataset["cells"]}
    missing = [name for name in HEADLINE_CELL_NAMES if name not in by_name]
    if missing:
        raise ValueError(f"headline dataset missing cells: {missing[:3]}")
    return [by_name[name] for name in HEADLINE_CELL_NAMES]


def club_range_rows(dataset: dict[str, Any]) -> list[ClubRangeRow]:
    """Return draw/fade minus straight ranges across the eight cells per club."""
    by_club: dict[str, list[dict[str, Any]]] = {key: [] for key in CLUB_LABELS}
    for cell in _lean0_cells(dataset):
        by_club[cell["club_id"]].append(cell)
    rows: list[ClubRangeRow] = []
    for club_id, label in CLUB_LABELS.items():
        club_cells = by_club[club_id]
        if len(club_cells) != 8:
            raise ValueError(f"{club_id} must have 8 zero-lean cells, got {len(club_cells)}")
        draw = [_pattern_interval(c, "Draw") for c in club_cells]
        fade = [_pattern_interval(c, "Fade") for c in club_cells]
        rows.append(
            {
                "club_id": club_id,
                "club_label": label,
                "draw_sg_min": min(item["estimate"] for item in draw),
                "draw_sg_max": max(item["estimate"] for item in draw),
                "draw_se_min": min(item["bootstrap_se"] for item in draw),
                "draw_se_max": max(item["bootstrap_se"] for item in draw),
                "fade_sg_min": min(item["estimate"] for item in fade),
                "fade_sg_max": max(item["estimate"] for item in fade),
                "fade_se_min": min(item["bootstrap_se"] for item in fade),
                "fade_se_max": max(item["bootstrap_se"] for item in fade),
                "condition_count": len(club_cells),
            }
        )
    return rows


def exclusion_summary(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Unsupported fractions for the 24 headline cells."""
    summary: list[dict[str, Any]] = []
    for cell in _lean0_cells(dataset):
        attempted_n = 10_000
        paired_n = int(cell["paired_n"])
        supported = [
            int(cell["geometry"][pattern]["supported_n"])
            for pattern in ("Straight", "Draw", "Fade")
        ]
        excluded_before_paired = attempted_n - paired_n
        unsupported_within_pair = paired_n - min(supported)
        summary.append(
            {
                "cell": cell["cell"],
                "club_id": cell["club_id"],
                "scoring_status": cell.get("scoring_status"),
                "attempted_n": attempted_n,
                "common_supported_n": paired_n,
                "supported_n_by_pattern": supported,
                "excluded_before_paired_n": excluded_before_paired,
                "excluded_before_paired_rate": excluded_before_paired / attempted_n,
                "unsupported_within_pair_n": unsupported_within_pair,
            }
        )
    return summary


def format_strokes(value: float) -> str:
    """Format small per-opportunity SG deltas without spurious precision."""
    if abs(value) < 0.01:
        return f"{value:+.5f}"
    return f"{value:+.3f}"


def format_se(value: float) -> str:
    """Format bootstrap-derived SE without collapsing small values to zero."""
    if value < 0.001:
        return f"{value:.5f}"
    return f"{value:.3f}"


def build_exclusion_markdown(rows: list[dict[str, Any]]) -> str:
    """Render the exclusion-summary markdown table for the shot-pattern article."""
    header = (
        "| Club | Conditions | Excluded Before Paired Scoring | Within-Pair Unsupported |\n"
        "|:--|--:|--:|--:|\n"
    )
    by_club: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_club.setdefault(row["club_id"], []).append(row)
    labels = {"driver": "Driver", "seven_iron": "Seven Iron", "pitching_wedge": "Pitching Wedge"}
    body = []
    for club_id, label in labels.items():
        club_rows = by_club[club_id]
        max_excluded = max(item["excluded_before_paired_rate"] for item in club_rows)
        max_within = max(item["unsupported_within_pair_n"] for item in club_rows)
        body.append(
            f"| {label} | {len(club_rows)} | {max_excluded * 100:.2f}% max | {max_within} shots max |"
        )
    note = (
        "\nEach headline condition attempts 10,000 shots per pattern. "
        "Excluded-before-paired counts unsupported impacts or flights removed before "
        "common paired scoring.\n"
    )
    return header + "\n".join(body) + note


def build_markdown_table(rows: list[ClubRangeRow]) -> str:
    """Render the scored comparison table for Quarto inclusion."""
    header = (
        "| Club | Draw − Straight SG | Draw MC SE | Fade − Straight SG | Fade MC SE |\n"
        "|:--|--:|--:|--:|--:|\n"
    )
    body = []
    for row in rows:
        draw = f"{format_strokes(row['draw_sg_min'])} to {format_strokes(row['draw_sg_max'])}"
        fade = f"{format_strokes(row['fade_sg_min'])} to {format_strokes(row['fade_sg_max'])}"
        draw_se = f"{format_se(row['draw_se_min'])} to {format_se(row['draw_se_max'])}"
        fade_se = f"{format_se(row['fade_se_min'])} to {format_se(row['fade_se_max'])}"
        body.append(f"| {row['club_label']} | {draw} | {draw_se} | {fade} | {fade_se} |")
    return header + "\n".join(body) + "\n"


def build_article_summary(data_dir: Path) -> dict[str, Any]:
    """Load vendored data and emit article-ready aggregates."""
    dataset = load_headline_dataset(data_dir)
    rows = club_range_rows(dataset)
    exclusions = exclusion_summary(dataset)
    return {
        "schema": "shot-pattern-article-summary/1",
        "source_dataset": "headline_paired_sg.csv",
        "bootstrap_resamples": dataset.get("bootstrap_resamples"),
        "club_ranges": rows,
        "exclusion_by_cell": exclusions,
        "markdown_table": build_markdown_table(rows),
        "exclusion_markdown": build_exclusion_markdown(exclusions),
    }
