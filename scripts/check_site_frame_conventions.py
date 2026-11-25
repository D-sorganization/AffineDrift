#!/usr/bin/env python3
"""Guard site frame and spatial-vector convention references (#5593)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent
NOTATION = ROOT / "NOTATION.md"
CONVENTIONS_PATH = ROOT / "data/agent/conventions.json"
UPSTREAM_PAGE = ROOT / "pages/upstreamdrift-conventions.qmd"
CANONICAL_ANCHOR = "coordinate-frame-conventions"

Y_UP_ARTICLES = (
    "articles/impact-mechanics-and-ball-flight.qmd",
    "articles/reference-point-problem.qmd",
    "articles/rotation-induced-spin.qmd",
    "articles/green-simulation.qmd",
)

REQUIRED_CONVENTION_IDS = (
    "site-default-z-up-frame",
    "spatial-twist-angular-first",
    "spatial-wrench-angular-first",
    "upstream-canonical-v2-si",
    "upstream-spatial-jacobian-order",
    "y-up-impact-target-frame",
)


def _errors_for_y_up_articles() -> list[str]:
    errors: list[str] = []
    for rel in Y_UP_ARTICLES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing article: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if CANONICAL_ANCHOR not in text:
            errors.append(f"{rel}: must link to {CANONICAL_ANCHOR}")
        if "upstreamdrift-conventions" not in text:
            errors.append(f"{rel}: must link to UpstreamDrift conventions page")
    return errors


def _errors_for_notation() -> list[str]:
    errors: list[str] = []
    if not NOTATION.is_file():
        return ["NOTATION.md missing"]
    text = NOTATION.read_text(encoding="utf-8")
    if f"{{#{CANONICAL_ANCHOR}}}" not in text and "### Coordinate Frame Conventions" not in text:
        errors.append("NOTATION.md missing coordinate frame section")
    if "Y-up impact" not in text:
        errors.append("NOTATION.md must name the Y-up impact / green variant")
    if "angular blocks first" not in text:
        errors.append("NOTATION.md must state angular-first spatial 6-vectors")
    return errors


def _errors_for_registry() -> list[str]:
    errors: list[str] = []
    if not CONVENTIONS_PATH.is_file():
        return [f"missing {CONVENTIONS_PATH.relative_to(ROOT)}"]
    payload = json.loads(CONVENTIONS_PATH.read_text(encoding="utf-8"))
    rows = {row["id"] for row in payload.get("conventions", []) if isinstance(row, dict)}
    for convention_id in REQUIRED_CONVENTION_IDS:
        if convention_id not in rows:
            errors.append(f"conventions.json missing id {convention_id!r}")
    return errors


def _errors_for_upstream_page() -> list[str]:
    errors: list[str] = []
    if not UPSTREAM_PAGE.is_file():
        return ["pages/upstreamdrift-conventions.qmd missing"]
    text = UPSTREAM_PAGE.read_text(encoding="utf-8")
    pin = "c8814a1b9d120ce382ee1de9a6583bb5ef569a15"
    if pin not in text:
        errors.append("upstreamdrift-conventions page missing pinned commit")
    if "#site-vs-code" not in text and "site-vs-code" not in text:
        errors.append("upstreamdrift-conventions page missing site-vs-code mapping")
    if "canonical-v2.md" not in text:
        errors.append("upstreamdrift-conventions must cite canonical-v2.md at pin")
    return errors


def collect_violations() -> list[str]:
    """Return all convention pinning violations."""
    errors: list[str] = []
    errors.extend(_errors_for_notation())
    errors.extend(_errors_for_registry())
    errors.extend(_errors_for_upstream_page())
    errors.extend(_errors_for_y_up_articles())
    return errors


def main() -> int:
    """Validate frame convention cross-links and registry rows."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    errors = collect_violations()
    if errors:
        for error in errors:
            LOGGER.error("%s", error)
        return 1
    LOGGER.info(
        "site frame conventions OK (%d Y-up articles, %d registry ids)",
        len(Y_UP_ARTICLES),
        len(REQUIRED_CONVENTION_IDS),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
