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
