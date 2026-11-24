#!/usr/bin/env python3
"""Attribute a Lighthouse report's cost to client-side math rendering (#5253).

Usage: ``python3 scripts/lighthouse_math_cost.py REPORT.json [REPORT2.json REPORT3.json]``

Reads one Lighthouse JSON report and prints the share of transfer size, script
boot-up time and render blocking that comes from MathJax-family scripts. It only
reads the report; it changes no site configuration.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

MATH_MARKERS = ("mathjax", "equation-runtime", "katex")
REPEAT_COUNT = 3
COMPARISON_FIELDS = ("requestedUrl", "finalDisplayedUrl", "lighthouseVersion", "configSettings")
REQUIRED_AUDITS = (
    "largest-contentful-paint",
    "total-blocking-time",
    "network-requests",
    "bootup-time",
    "render-blocking-resources",
)


def _is_math(url: str) -> bool:
    lowered = url.lower()
    return any(marker in lowered for marker in MATH_MARKERS)


def _items(audits: dict[str, Any], name: str) -> list[dict[str, Any]]:
    return list(audits.get(name, {}).get("details", {}).get("items", []))


def math_cost(lhr: dict[str, Any]) -> dict[str, float]:
    """Return the math-rendering share of one Lighthouse report.

    Precondition: ``lhr`` is a Lighthouse result (has ``audits``).
    Postcondition: every value is a number; absent audits count as zero.
    """
    if "audits" not in lhr or "categories" not in lhr:
        raise ValueError("not a Lighthouse report: missing 'audits' or 'categories'")
    audits = lhr["audits"]
    requests = _items(audits, "network-requests")
    bootup = [i for i in _items(audits, "bootup-time") if _is_math(i["url"])]
    blocking = [i for i in _items(audits, "render-blocking-resources") if _is_math(i["url"])]
    return {
        "performance_score": lhr["categories"]["performance"]["score"],
        "lcp_ms": audits.get("largest-contentful-paint", {}).get("numericValue", 0.0),
        "tbt_ms": audits.get("total-blocking-time", {}).get("numericValue", 0.0),
        "total_transfer_bytes": sum(r.get("transferSize", 0) for r in requests),
        "math_transfer_bytes": sum(
            r.get("transferSize", 0) for r in requests if _is_math(r["url"])
        ),
        "math_bootup_ms": sum(i["total"] for i in bootup),
        "math_scripting_ms": sum(i["scripting"] for i in bootup),
        "math_render_blocking_ms": sum(i.get("wastedMs", 0) for i in blocking),
    }


def _repeat_metrics(report: dict[str, Any]) -> dict[str, float]:
    """Reject failed or incomplete repeat runs instead of treating missing audits as zero."""
    audits = report.get("audits", {})
    if report.get("runtimeError") or any(name not in audits for name in REQUIRED_AUDITS):
        raise ValueError("repeat report contains a runtime error or missing audit")
    if any(
        audits[name].get("errorMessage") or audits[name].get("scoreDisplayMode") == "error"
        for name in REQUIRED_AUDITS
    ):
        raise ValueError("repeat report contains a failed required audit")
    if any("numericValue" not in audits[name] for name in REQUIRED_AUDITS[:2]):
        raise ValueError("repeat report contains an audit without its numeric result")
    values = math_cost(report)
    if any(
        not isinstance(value, (int, float)) or not math.isfinite(value) for value in values.values()
    ):
        raise ValueError("repeat report metrics must be finite numbers")
    return values


def repeat_math_cost(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize three independent, comparable Lighthouse runs without a causal SSR claim.

    Preconditions: identical URLs, Lighthouse version and settings; distinct fetch times.
    Postcondition: each metric retains its min, median and max plus all per-run values.
    """
    if len(reports) != REPEAT_COUNT:
        raise ValueError("exactly three Lighthouse reports are required")
    baseline = {field: reports[0].get(field) for field in COMPARISON_FIELDS}
    if any(value is None or value == "" for value in baseline.values()):
        raise ValueError("repeat reports require URL, version and settings provenance")
    if any(
        {field: report.get(field) for field in COMPARISON_FIELDS} != baseline for report in reports
    ):
        raise ValueError("repeat reports must use identical URLs, Lighthouse version and settings")
    times = [report.get("fetchTime") for report in reports]
    if (
        any(not isinstance(time, str) or not time for time in times)
        or len(set(times)) != REPEAT_COUNT
    ):
        raise ValueError("repeat reports require three distinct fetchTime values")
    metrics = [_repeat_metrics(report) for report in reports]
    return {
        **baseline,
        "run_count": REPEAT_COUNT,
        "runs": [
            {"fetchTime": time, "metrics": values, "warnings": report.get("runWarnings", [])}
            for time, values, report in zip(times, metrics, reports, strict=True)
        ],
        "metrics": {
            key: {
                "min": min(values[key] for values in metrics),
                "median": statistics.median(values[key] for values in metrics),
                "max": max(values[key] for values in metrics),
            }
            for key in metrics[0]
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (1, REPEAT_COUNT):
        print(__doc__)
        return 2
    if len(args) == REPEAT_COUNT:
        reports = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args]
        sys.stdout.write(json.dumps(repeat_math_cost(reports), indent=2, allow_nan=False) + "\n")
        return 0
    report = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    for key, value in math_cost(report).items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
