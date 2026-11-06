#!/usr/bin/env python3
"""Attribute a Lighthouse report's cost to client-side math rendering (#5253).

Usage: ``python3 scripts/lighthouse_math_cost.py REPORT.json``

Reads one Lighthouse JSON report and prints the share of transfer size, script
boot-up time and render blocking that comes from MathJax-family scripts. It only
reads the report; it changes no site configuration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MATH_MARKERS = ("mathjax", "equation-runtime", "katex")


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


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__)
        return 2
    report = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    for key, value in math_cost(report).items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
