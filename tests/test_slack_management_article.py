"""Contract tests for "Managing Slack in Linked Systems" (#5135).

Every number the article quotes from the synthetic studies is formatted from
``data/slack_management/results.json`` and must appear verbatim in the page, so the prose
cannot drift from the code.  Scope boundaries and review findings (PR #5140) are pinned too.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import validate_article_frontmatter

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/slack-management-linked-systems.qmd"
DATA = ROOT / "data/slack_management/results.json"
TEXT = ARTICLE.read_text(encoding="utf-8")
SECTIONS: dict[str, Any] = json.loads(DATA.read_text(encoding="utf-8"))["sections"]
REPS = SECTIONS["representations"]["representations"]
FLIP = SECTIONS["flip"]
SPLIT = SECTIONS["split"]["representations"]
PAIRS = SECTIONS["split"]["internal_pair_grid_nm"]


def fixed(value: float, places: int) -> str:
    return f"{value:.{places}f}"


def percent(value: float) -> str:
    return f"{100 * value:.0f}%"


def ms(value: float) -> str:
    return f"{1000 * value:.1f} ms"


def mrad(value: float) -> str:
    return f"{1000 * value:.2g} mrad"


def at_pair(rep: str, key: str, pair: float) -> float:
    value: float = SPLIT[rep][key][PAIRS.index(pair)]
    return value


def _representation_rows() -> list[str]:
    rows = []
    for name in REPS:
        persistent, reversal = REPS[name]["persistent_direction"], REPS[name]["role_reversal"]
        cells = [
            fixed(persistent["error_impulse_nms"], 4),
            fixed(reversal["error_impulse_nms"], 4),
            percent(abs(REPS[name]["relative_advantage"])),
            f"{fixed(persistent['channel_error_impulse_nms'], 3)} / "
            f"{fixed(reversal['channel_error_impulse_nms'], 3)}",
        ]
        rows.extend(cells)
    return rows


def _quoted_values() -> list[str]:
    reproduction = SECTIONS["reproduction"]
    lags = SECTIONS["unequal_lags"]
    thresholds = FLIP["gap_thresholds_rad"]
    published = reproduction["published_nms"]
    verdicts = reproduction["grid_verdicts"]
    unequal = REPS["rigid_unequal_lags"]["role_reversal"]
    zero_12 = [FLIP["curves"][f"dead_zone_{p}ms"]["max_zero_transmission_s"] for p in (8, 18, 35)]
    index_12 = FLIP["gap_grid_rad"].index(0.012)
    return [
        *_representation_rows(),
        fixed(published["persistent_direction_preloaded"], 4),
        fixed(published["role_reversal_preloaded"], 4),
        f"{verdicts['persistent_favoured']} favour persistent direction",
        f"{verdicts['equivalent']} (all with zero dead zone) are equivalent",
        fixed(unequal["peak_overshoot_nm"], 2),
        f"${lags['exact_min_difference_nm']:.2f}$ N m",
        f"${lags['simulated_min_difference_nm']:.2f}$ N m at {1000 * lags['simulated_min_time_s']:.1f}",
        f"{1000 * lags['exact_min_time_s']:.2f}$ ms",
        *(mrad(thresholds["dead_zone"][m]) for m in ("0.01", "0.05", "0.1")),
        *(f"{1000 * thresholds['smooth'][m]:.2g}" for m in ("0.01", "0.05", "0.1")),
        f"by {1000 * FLIP['reference_stretch_rad']:.0f} mrad",
        *(f"{1000 * curve[index_12]:.1f}" for curve in zero_12),
        ms(REPS["dead_zone"]["role_reversal"]["recovery_delay_s"][1]),
        fixed(at_pair("dead_zone", "error_impulse_nms", 10.0), 4),
        fixed(at_pair("smooth_stiffening", "error_impulse_nms", 9.0), 4),
        fixed(at_pair("dead_zone", "peak_overshoot_nm", 10.0), 2) + " N m",
        fixed(at_pair("smooth_stiffening", "channel_error_impulse_nms", 20.0), 4),
    ]


@pytest.mark.parametrize("quoted", _quoted_values())
def test_every_quoted_number_matches_the_data(quoted: str) -> None:
    assert quoted in TEXT


def test_muscle_margin_is_quoted_to_two_decimals() -> None:
    value = 100 * SECTIONS["muscle_margin"]["relative_advantage"]
    assert f"{value:.2f}%" == "0.96%" and "0.96%" in TEXT


def test_best_splits_and_floors_match_the_data() -> None:
    assert SPLIT["dead_zone"]["best_internal_pair_nm"] == 10.0
    assert SPLIT["smooth_stiffening"]["best_internal_pair_nm"] == 9.0
    assert SPLIT["dead_zone"]["channel_floor_pairs_nm"] == [16.0, 17.0, 18.0, 19.0, 20.0]
    plateau = SPLIT["dead_zone"]["error_impulse_nms"][PAIRS.index(11.0) :]
    assert max(plateau) - min(plateau) < 1e-9 and "from 11 to 24 N m" in TEXT


def test_front_matter_is_valid_and_registers_the_bibliography() -> None:
    front, _ = split_frontmatter(TEXT)
    assert validate_article_frontmatter(front, "articles/slack-management-linked-systems.qmd") == []
    assert "../references/slack-management.bib" in front["bibliography"]


@pytest.mark.parametrize(
    "required",
    [
        "https://github.com/D-sorganization/AffineDrift/issues/5134",
        "https://github.com/D-sorganization/AffineDrift/issues/5136",
        "https://github.com/D-sorganization/AffineDrift/pull/5140",
        "memoryless dead-zone-plus-damping surrogate",
        "1.96% in normalized output RMSE",
        "`maximum_transition_count = 0`",
        "TODO(source)",
    ],
)
def test_scope_and_review_findings_are_stated(required: str) -> None:
    assert required in TEXT


@pytest.mark.parametrize("forbidden", ["Bosch", "15–40 ms", "15-40 ms", "11 of 12"])
def test_removed_or_contradicted_figures_are_absent(forbidden: str) -> None:
    assert forbidden not in TEXT
