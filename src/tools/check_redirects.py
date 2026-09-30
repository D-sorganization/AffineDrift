"""Verify URL stability across deploys (WEB-02.9, #4503).

Consolidation and renaming move URLs. This module compares the manifest
of the previously deployed site against the current build's manifest and
the redirect ledger in ``config/redirects.yml``, failing the deploy when a
previously published route disappears without a documented, rendered
redirect.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from src.core.contracts import require
from src.tools.utils import setup_logging

logger = setup_logging(__name__, format_string="%(message)s")

DEFAULT_REDIRECTS_LEDGER = Path("config/redirects.yml")


def manifest_routes(manifest: dict[str, Any]) -> set[str]:
    """Return the set of published routes recorded in a public-site manifest."""
    return {page["route"] for page in manifest.get("pages", [])}


def load_redirect_ledger(ledger_path: Path) -> dict[str, str]:
    """Load the redirect ledger as a mapping of old route to new route.

    An absent ledger means no redirects have been recorded yet, which is
    valid. A ledger entry missing ``from`` or ``to`` is a documentation
    defect and fails loudly rather than being skipped silently.
    """
    if not ledger_path.exists():
        return {}

    data = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
    entries = data.get("redirects") or []
    redirects: dict[str, str] = {}
    for entry in entries:
        require(
            isinstance(entry, dict) and "from" in entry and "to" in entry,
            f"redirect ledger entry must have 'from' and 'to': {entry!r}",
        )
        redirects[entry["from"]] = entry["to"]
    return redirects


def find_unredirected_removed_routes(
    previous_manifest: dict[str, Any],
    current_manifest: dict[str, Any],
    redirects: dict[str, str],
) -> list[str]:
    """Return previously published routes missing from the current build with no redirect.

    A removed route is safe only when the redirect ledger documents where
    it now points.
    """
    removed = manifest_routes(previous_manifest) - manifest_routes(current_manifest)
    return sorted(route for route in removed if route not in redirects)


def verify_redirect_targets_rendered(redirects: dict[str, str], docs_dir: Path) -> list[str]:
    """Return ledger entries whose old route was never actually rendered.

    A ledger entry only proves URL stability once Quarto's ``aliases:``
    mechanism produced a static file at the old route; a declared-but-not
    -rendered entry would leave the old URL a dead link.
    """
    unrendered = []
    for old_route in redirects:
        rendered_path = docs_dir / old_route.lstrip("/")
        if not rendered_path.is_file():
            unrendered.append(old_route)
    return sorted(unrendered)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous-manifest", type=Path, required=True)
    parser.add_argument("--current-manifest", type=Path, required=True)
    parser.add_argument("--redirects", type=Path, default=DEFAULT_REDIRECTS_LEDGER)
    parser.add_argument("--docs-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main() -> int:
    """Compare deploy manifests and fail when a route vanished without a verified redirect."""
    args = _parse_args()

    if not args.previous_manifest.is_file():
        logger.info(
            "No previous deploy manifest at %s (first deploy or unreachable); "
            "skipping URL stability comparison.",
            args.previous_manifest,
        )
        return 0

    previous_manifest = json.loads(args.previous_manifest.read_text(encoding="utf-8"))
    current_manifest = json.loads(args.current_manifest.read_text(encoding="utf-8"))
    redirects = load_redirect_ledger(args.redirects)

    missing = find_unredirected_removed_routes(previous_manifest, current_manifest, redirects)
    if missing:
        logger.error("Routes removed without a redirects.yml entry:")
        for route in missing:
            logger.error("  %s", route)
        return 1

    if args.docs_dir is not None:
        unrendered = verify_redirect_targets_rendered(redirects, args.docs_dir)
        if unrendered:
            logger.error("Redirect ledger entries with no rendered alias output:")
            for route in unrendered:
                logger.error("  %s", route)
            return 1

    logger.info("All previously published routes remain reachable or have a verified redirect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
