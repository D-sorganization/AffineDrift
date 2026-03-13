#!/usr/bin/env python3
"""Synchronize canonical frontend assets to mirrored locations.

This repository has historical duplication across root/src/docs trees.
To control drift safely, we synchronize only explicitly-mapped files that are
expected to remain byte-identical.

Usage:
  python3 scripts/sync_frontend_assets.py           # apply sync
  python3 scripts/sync_frontend_assets.py --check   # fail on drift
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SyncMap:
    source: str
    mirrors: tuple[str, ...]


SYNC_MAPS: tuple[SyncMap, ...] = (
    SyncMap(
        source="css/startup-launcher.css",
        mirrors=("src/css/startup-launcher.css", "docs/css/startup-launcher.css"),
    ),
    SyncMap(
        source="css/search-metrics.css",
        mirrors=("src/css/search-metrics.css", "docs/css/search-metrics.css"),
    ),
    SyncMap(
        source="css/print.css",
        mirrors=("src/css/print.css", "docs/css/print.css"),
    ),
    SyncMap(
        source="css/bibliography.css",
        mirrors=("src/css/bibliography.css", "docs/css/bibliography.css"),
    ),
    SyncMap(
        source="css/critics-corner.css",
        mirrors=("src/css/critics-corner.css", "docs/css/critics-corner.css"),
    ),
    SyncMap(
        source="css/resources.css",
        mirrors=("src/css/resources.css", "docs/css/resources.css"),
    ),
    # js/ is the canonical source; docs/js/ is the Quarto-served mirror.
    # src/js/ has been removed (issue #1425); js/ syncs directly to docs/js/.
    SyncMap(
        source="js/metrics.js",
        mirrors=("docs/js/metrics.js",),
    ),
    SyncMap(
        source="js/startup-launcher.js",
        mirrors=("docs/js/startup-launcher.js",),
    ),
    SyncMap(
        source="js/notes-workspace.js",
        mirrors=("docs/js/notes-workspace.js",),
    ),
    SyncMap(
        source="js/bibliography.js",
        mirrors=("docs/js/bibliography.js",),
    ),
    SyncMap(
        source="styles.css",
        mirrors=("docs/styles.css",),
    ),
)

# These are intentionally different architectures and are not synchronized.
INTENTIONAL_DIVERGENCE: tuple[str, ...] = ("script.js vs docs/script.js",)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_one(repo_root: Path, mapping: SyncMap, check_only: bool) -> list[str]:
    source = repo_root / mapping.source
    if not source.exists():
        return [f"MISSING SOURCE: {mapping.source}"]

    issues: list[str] = []
    src_hash = sha256(source)

    for mirror_rel in mapping.mirrors:
        mirror = repo_root / mirror_rel
        mirror.parent.mkdir(parents=True, exist_ok=True)

        if not mirror.exists():
            if check_only:
                issues.append(f"MISSING MIRROR: {mirror_rel}")
            else:
                shutil.copy2(source, mirror)
                issues.append(f"SYNCED: {mapping.source} -> {mirror_rel}")
            continue

        mirror_hash = sha256(mirror)
        if mirror_hash != src_hash:
            if check_only:
                issues.append(f"DRIFT: {mapping.source} != {mirror_rel}")
            else:
                shutil.copy2(source, mirror)
                issues.append(f"SYNCED: {mapping.source} -> {mirror_rel}")

    return issues


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Sync canonical frontend assets")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: report drift and exit non-zero without modifying files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    logger.info("Canonical sync maps:")
    for m in SYNC_MAPS:
        logger.info("- %s -> %s", m.source, ", ".join(m.mirrors))

    logger.info("Intentional divergence (not synced):")
    for item in INTENTIONAL_DIVERGENCE:
        logger.info("- %s", item)

    findings: list[str] = []
    for mapping in SYNC_MAPS:
        findings.extend(sync_one(repo_root, mapping, check_only=args.check))

    if not findings:
        logger.info("No drift detected.")
        return 0

    logger.info("Findings:")
    for f in findings:
        logger.info("- %s", f)

    if args.check:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
