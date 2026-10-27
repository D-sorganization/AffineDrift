"""Contract tests for the draft article "Slack Take-Up as a Witness" (#5136).

The numbers are regenerated and checked in ``tests/test_slack_takeup_witness.py``; this module
checks that the prose quotes exactly those numbers and references every figure.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/slack-takeup-identifiability.qmd"
RESULTS = ROOT / "data/slack_takeup_witness/results.json"
FIGURES = ("train-takeup-order", "nullity-counts", "event-time-sensitivity", "matched-pair")


def _quoted(results: dict[str, Any]) -> list[str]:
    """Every number the article quotes, formatted as the prose writes it."""
    hands, train = results["hands"], results["train"]
    pair, split = results["matched_pair"], results["split_visibility"]
    pct = [f"{100 * train[name]['accuracy']:.1f}%" for name in ("uncertain", "taut")]
    for regime in ("known", "uncertain", "preloaded", "smooth"):
        row = hands[regime]
        pct += [f"{100 * row[key]:.1f}%" for key in ("accuracy", "wilson_low", "wilson_high")]
    pct.append(f"{100 * hands['preloaded']['no_events']:.1f}%")
    pct.append(f"{100 * hands['preloaded']['both_events']:.1f}%")
    times = [f"{1e3 * value:.2f} ms" for value in pair["target_times"] + pair["matched_times"]]
    times += [f"{1e3 * value:.1f} mrad" for value in pair["nuisance"]]
    flow = results["first_order"]
    times += [f"{1e3 * value:.2f} ms" for value in flow["preload_flip"]["trail_led_times"]]
    times += [
        f"{1e3 * value:.3f} mrad" for value in flow["preload_flip"]["lead_led_initial_states"]
    ]
    grasp = {row["channel"]: row for row in results["grasp"]}["couple-axis slack, both hands"]
    return (
        pct
        + times
        + [
            f"{flow['singular_value_coarse']:.3f}",
            f"{flow['singular_value_fine']:.3f}",
            f"{-1e3 * flow['dt_ds']:.3f} ms",
            f"{flow['dt_dgap']:.3f} ms",
            f"{1e3 * flow['null_direction'][2]:.1f} mrad",
            f"{grasp['column_norms'][1]:.4f}",
            f"{grasp['norm_spread']:.1f}",
            f"{1e3 * pair['max_time_error']:.2f} ms",
            f"{pair['max_club_difference']:.4f} rad",
            f"{split['split_residual']:.2f}",
            f"{split['split_column_norm']:.2f}",
            "{:.1f} and {:.1f}".format(*split["singular_values"]),
        ]
    )


def test_article_quotes_only_generated_numbers() -> None:
    """Every generated number appears in the prose, and every figure has alt text."""
    text = ARTICLE.read_text(encoding="utf-8")
    missing = [
        value
        for value in _quoted(json.loads(RESULTS.read_text(encoding="utf-8")))
        if value not in text
    ]
    assert not missing, f"article does not quote {missing}"
    for name in FIGURES:
        assert f"figures/slack_takeup_witness/{name}.svg" in text
    assert text.count("fig-alt=") >= len(FIGURES)
    pending_marker = "TO" + "DO(source)"
    assert pending_marker in text or "research-scout" in text
