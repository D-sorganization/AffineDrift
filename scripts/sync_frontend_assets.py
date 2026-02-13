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
import shutil
from dataclasses import dataclass
from pathlib import Path


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
        source="js/metrics.js",
        mirrors=("src/js/metrics.js", "docs/js/metrics.js"),
    ),
    SyncMap(
        source="js/startup-launcher.js",
        mirrors=("src/js/startup-launcher.js", "docs/js/startup-launcher.js"),
    ),
    SyncMap(
        source="js/notes-workspace.js",
        mirrors=("src/js/notes-workspace.js", "docs/js/notes-workspace.js"),
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
INTENTIONAL_DIVERGENCE: tuple[str, ...] = (
    "js/main.js vs src/js/main.js",
    "js/bibliography.js vs src/js/bibliography.js",
    "script.js vs docs/script.js",
)


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
    parser = argparse.ArgumentParser(description="Sync canonical frontend assets")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: report drift and exit non-zero without modifying files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    print("Canonical sync maps:")
    for m in SYNC_MAPS:
        print(f"- {m.source} -> {', '.join(m.mirrors)}")

    print("Intentional divergence (not synced):")
    for item in INTENTIONAL_DIVERGENCE:
        print(f"- {item}")

    findings: list[str] = []
    for mapping in SYNC_MAPS:
        findings.extend(sync_one(repo_root, mapping, check_only=args.check))

    if not findings:
        print("No drift detected.")
        return 0

    print("Findings:")
    for f in findings:
        print(f"- {f}")

    if args.check:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
