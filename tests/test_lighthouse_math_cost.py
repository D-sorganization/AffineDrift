"""#5253: attribute Lighthouse cost to client-side math rendering."""

from __future__ import annotations

import pytest

from scripts.lighthouse_math_cost import math_cost

MJ = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"
LAZY = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/ui/lazy.js"


def _lhr() -> dict:
    return {
        "categories": {"performance": {"score": 0.37}},
        "audits": {
            "largest-contentful-paint": {"numericValue": 9800.0},
            "total-blocking-time": {"numericValue": 760.0},
            "network-requests": {
                "details": {
                    "items": [
                        {"url": "http://localhost:8000/x.html", "transferSize": 1000},
                        {"url": MJ, "transferSize": 200000},
                        {"url": LAZY, "transferSize": 3000},
                    ]
                }
            },
            "bootup-time": {
                "details": {
                    "items": [
                        {"url": MJ, "total": 900.0, "scripting": 500.0},
                        {"url": LAZY, "total": 300.0, "scripting": 250.0},
                        {"url": "http://localhost:8000/x.html", "total": 2000.0, "scripting": 70.0},
                    ]
                }
            },
            "render-blocking-resources": {
                "details": {
                    "items": [{"url": MJ, "wastedMs": 0}, {"url": "a.css", "wastedMs": 500}]
                }
            },
        },
    }


def test_math_cost_attributes_transfer_and_bootup() -> None:
    cost = math_cost(_lhr())
    assert cost["math_transfer_bytes"] == 203000
    assert cost["total_transfer_bytes"] == 204000
    assert cost["math_bootup_ms"] == 1200.0
    assert cost["math_scripting_ms"] == 750.0
    assert cost["performance_score"] == 0.37
    assert cost["tbt_ms"] == 760.0


def test_math_cost_reports_render_blocking_math_waste() -> None:
    assert math_cost(_lhr())["math_render_blocking_ms"] == 0


def test_math_cost_rejects_a_non_lighthouse_report() -> None:
    with pytest.raises(ValueError, match="Lighthouse"):
        math_cost({"foo": 1})


def _repeats() -> list[dict]:
    reports = [_lhr() for _ in range(3)]
    for index, report in enumerate(reports):
        report.update(
            requestedUrl="https://affinedrift.com/articles/theory-part1.html",
            finalDisplayedUrl="https://affinedrift.com/articles/theory-part1.html",
            lighthouseVersion="12.6.1",
            fetchTime=f"2026-11-06T20:0{index}:00Z",
            configSettings={"formFactor": "mobile", "throttlingMethod": "simulate"},
        )
        report["audits"]["total-blocking-time"]["numericValue"] = [900, 100, 500][index]
    return reports


def test_repeat_summary_reports_spread_and_preserves_run_evidence() -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    result = repeat_math_cost(reports)
    assert result["run_count"] == 3
    assert result["metrics"]["tbt_ms"] == {"min": 100, "median": 500, "max": 900}
    assert result["runs"][0]["fetchTime"] == reports[0]["fetchTime"]
    assert result["runs"][0]["metrics"]["tbt_ms"] == 900
    assert result["configSettings"] == reports[0]["configSettings"]


@pytest.mark.parametrize("count", [0, 1, 2, 4])
def test_repeat_summary_requires_three_runs(count: int) -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    with pytest.raises(ValueError, match="three"):
        repeat_math_cost((_repeats() * 2)[:count])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("requestedUrl", "https://example.org/other"),
        ("finalDisplayedUrl", "https://example.org/redirected"),
        ("lighthouseVersion", "13.0.0"),
        ("configSettings", {"formFactor": "desktop"}),
        ("fetchTime", "2026-11-06T20:00:00Z"),
    ],
)
def test_repeat_summary_rejects_incomparable_or_duplicate_runs(field: str, value: object) -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    reports[1][field] = value
    with pytest.raises(ValueError):
        repeat_math_cost(reports)


@pytest.mark.parametrize("value", [None, float("nan"), float("inf")])
def test_repeat_summary_rejects_failed_metric(value: float | None) -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    reports[1]["categories"]["performance"]["score"] = value
    with pytest.raises(ValueError, match="finite"):
        repeat_math_cost(reports)


def test_repeat_summary_rejects_missing_metric_audit() -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    del reports[1]["audits"]["total-blocking-time"]
    with pytest.raises(ValueError, match="audit"):
        repeat_math_cost(reports)


@pytest.mark.parametrize("audit", ["bootup-time", "total-blocking-time"])
def test_repeat_summary_rejects_failed_required_audit(audit: str) -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    reports[1]["audits"][audit] = {"scoreDisplayMode": "error", "errorMessage": "trace failed"}
    with pytest.raises(ValueError, match="audit"):
        repeat_math_cost(reports)


def test_repeat_summary_preserves_lighthouse_warnings() -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    reports[1]["runWarnings"] = ["Test warning"]
    assert repeat_math_cost(reports)["runs"][1]["warnings"] == ["Test warning"]


def test_repeat_summary_rejects_missing_numeric_result() -> None:
    from scripts.lighthouse_math_cost import repeat_math_cost

    reports = _repeats()
    del reports[1]["audits"]["total-blocking-time"]["numericValue"]
    with pytest.raises(ValueError, match="audit"):
        repeat_math_cost(reports)
