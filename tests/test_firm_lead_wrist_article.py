"""Contract tests for the firm-lead-wrist preload article (#5134)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "articles/firm-lead-wrist-preload.qmd"
FIGURE_DIR = ROOT / "articles/figures/lead_wrist_preload"
FIGURES = ("fig_preload_two_models", "fig_preload_robustness", "fig_internal_wrench")
FIGURES += ("fig_impact_timescales",)


@pytest.mark.parametrize(
    "quoted",
    ["0.0717", "0.1954", "0.2011", "11.5 ms", "22.0 ms", "0.08998", "0.09084", "0.94%"]
    + ["0.00277", "0.000514", "445 microseconds", "172%", "0.4%", "0.1505", "0.1918"]
    + ["10.80 N m", "@kao1995"],
)
def test_article_quotes_reproduced_numbers(quoted: str) -> None:
    assert quoted in ARTICLE_PATH.read_text(encoding="utf-8")


def test_article_cites_no_unverified_quote_marker_left_unlisted() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert text.count("TODO(source") == text.count("TODO(source, #5134)")


@pytest.mark.parametrize("stem", FIGURES)
def test_article_figures_are_committed_and_referenced(stem: str) -> None:
    assert (FIGURE_DIR / f"{stem}.svg").is_file()
    assert f"figures/lead_wrist_preload/{stem}.svg" in ARTICLE_PATH.read_text(encoding="utf-8")


def test_dead_zone_result_is_not_presented_alone() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert text.index("0.08998") - text.index("0.1954") < 2000
    assert "@jobe1995" not in text
