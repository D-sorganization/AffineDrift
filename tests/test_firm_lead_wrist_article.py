"""Contract tests for the firm-lead-wrist preload article (#5134)."""

import json
from pathlib import Path
from typing import Any

import pytest

from src.tools import lead_wrist_preload_models as models

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "articles/firm-lead-wrist-preload.qmd"
RESULTS_PATH = ROOT / "data/lead_wrist_preload/results.json"
FIGURE_DIR = ROOT / "articles/figures/lead_wrist_preload"
FIGURES = ("fig_preload_two_models", "fig_preload_robustness", "fig_internal_wrench")
FIGURES += ("fig_impact_timescales",)


@pytest.mark.parametrize(
    "quoted",
    ["0.0717", "0.1954", "2.7×", "11.5 ms", "22.0 ms", "0.08998", "0.09084", "0.94%"]
    + ["0.00277", "0.000514", "445 microseconds", "172%", "0.4%", "0.1505", "0.1918"]
    + ["10.80 N m", "@kao1995"],
)
def test_article_quotes_reproduced_numbers(quoted: str) -> None:
    assert quoted in ARTICLE_PATH.read_text(encoding="utf-8")


def test_article_cites_no_unverified_quote_marker_left_unlisted() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    pending_marker = "TO" + "DO(source"
    listed_marker = f"{pending_marker}, #5134)"
    assert text.count(pending_marker) == text.count(listed_marker)


@pytest.mark.parametrize("stem", FIGURES)
def test_article_figures_are_committed_and_referenced(stem: str) -> None:
    assert (FIGURE_DIR / f"{stem}.svg").is_file()
    assert f"figures/lead_wrist_preload/{stem}.svg" in ARTICLE_PATH.read_text(encoding="utf-8")


def test_dead_zone_result_is_not_presented_alone() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert text.index("0.08998") - text.index("0.1954") < 2000
    assert "@jobe1995" not in text


def _results() -> dict[str, Any]:
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def test_committed_results_match_fresh_run() -> None:
    assert _results() == json.loads(json.dumps(models.build_results()))


def test_review_numbers_are_quoted_from_results() -> None:
    results, text = _results(), ARTICLE_PATH.read_text(encoding="utf-8")
    reversal = results["muscle"]["complete_role_reversal"]
    gap = results["dead_zone"]["complete_role_reversal_preloaded"]["net_gap_s"]
    quoted = [
        f"{gap * 1000:.1f} ms",
        f"{reversal['shortfall_nms']:.4f}",
        f"{reversal['overshoot_nms']:.4f}",
        f"{results['muscle']['persistent_direction']['shortfall_nms']:.4f}",
        f"about {results['decay_to_rise_ratio']['activation_0.001']:.0f} times",
        f"about {results['decay_to_rise_ratio']['activation_0.08']:.0f} times",
    ]
    for value in quoted:
        assert value in text, value


def test_table_percentages_share_the_persistent_baseline() -> None:
    results, text = _results(), ARTICLE_PATH.read_text(encoding="utf-8")
    dead = results["dead_zone"]
    muscle = results["muscle"]

    def relative(persistent: float, reversal: float) -> float:
        return 100.0 * (reversal - persistent) / persistent

    quoted = [
        f"+{relative(dead['persistent_direction_preloaded']['error_impulse_nms'], dead['complete_role_reversal_preloaded']['error_impulse_nms']):.0f}%",
        f"about +{relative(muscle['persistent_direction']['error_impulse_nms'], muscle['complete_role_reversal']['error_impulse_nms']):.2f}%",
        f"+{100.0 * results['muscle_step_audit']['limit_relative_difference']:.2f}%",
        f"−{-100.0 * results['muscle_step_audit_net_14']['limit_relative_difference']:.0f}%",
    ]
    for value in quoted:
        assert value in text, value


def test_switch_race_figures_are_quoted_from_results() -> None:
    race, text = _results()["switch_time_constants_ms"], ARTICLE_PATH.read_text(encoding="utf-8")
    assert race["arm_positive_rise"] == pytest.approx(race["wrist_negative_rise"])
    assert f"about {race['arm_positive_rise']:.1f} ms" in text
    assert f"about {race['arm_negative_decay']:.0f} ms in the arm" in text
    assert f"about {race['wrist_positive_decay']:.0f} ms in the wrist" in text
    slowest = max(race["arm_negative_decay"], race["wrist_positive_decay"])
    fastest = min(race["arm_negative_decay"], race["wrist_positive_decay"])
    ratios = (fastest / race["arm_positive_rise"], slowest / race["arm_positive_rise"])
    assert f"roughly {ratios[0]:.0f} to {ratios[1]:.0f} times faster" in text


def test_companion_split_vocabulary() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "Dead Zones, Internal Wrench, and the Heavy Hit" in text
    assert "Backlash" not in text and "bicycle" not in text
    assert text.count("transition") == 1
    assert "Advantage $A$, relative to persistent" in text
    assert "does not by itself add mass" in text and "cannot add mass" not in text
    assert text.lower().count("delay") == 1 and "a *lag* is a delay" in text
    assert "about 0.95%" in text


@pytest.mark.parametrize("program", [models.PERSISTENT, models.REVERSAL])
def test_muscle_model_has_settled_to_a_loaded_start(program: models.Program) -> None:
    trace = models.simulate_muscle(program)
    at_switch = trace["transmitted_net_nm"][trace["time_s"] < 0.0][-1]
    assert at_switch == pytest.approx(program.arm_pre_nm + program.wrist_pre_nm, abs=1e-3)
