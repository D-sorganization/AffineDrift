#!/usr/bin/env python3
"""Update service worker cache version using a content hash.

Computes a short hash of key static assets (JS and CSS files) and updates
the CACHE_NAME in service-worker.js to include it. This provides automatic
cache invalidation when static assets change.

Part of the content-hash cache busting solution (issue #1459).

Usage:
    python3 scripts/update_sw_cache_version.py [--dry-run]
"""

import argparse
import hashlib
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
SW_FILE = ROOT / "service-worker.js"

# Files whose changes should invalidate the cache.
# NOTE: these must be real repo-root-relative paths — missing entries are
# silently skipped, which previously meant CSS changes never bumped the
# cache version (the old list pointed at css/styles.css and css/base.css,
# neither of which exists). tests/test_update_sw_cache_version.py guards
# against this regressing.
# (service-worker.js itself is deliberately excluded: this script rewrites
# CACHE_NAME inside it, so hashing it would make the hash non-idempotent.)
HASH_SOURCES = [
    "styles.css",
    "custom.scss",
]

# Glob patterns (repo-root-relative) whose matches are hashed as well, so
# every runtime stylesheet and script participates in cache invalidation.
HASH_GLOBS = [
    "js/*.js",
    "css/**/*.css",
]

CACHE_NAME_PATTERN = re.compile(r"(const CACHE_NAME\s*=\s*'affinedrift-)([^']+)(')")


def iter_hash_files(root: Path = ROOT) -> list[Path]:
    """Return the deterministic, sorted list of files included in the hash."""
    files = [root / rel_path for rel_path in HASH_SOURCES]
    for pattern in HASH_GLOBS:
        files.extend(p for p in root.glob(pattern) if p.is_file())
    # Deterministic order regardless of filesystem enumeration order.
    return sorted(set(files))


def compute_asset_hash(root: Path = ROOT) -> str:
    """Compute a short hash of the key static assets."""
    hasher = hashlib.sha256()
    for path in iter_hash_files(root):
        if path.exists():
            hasher.update(path.relative_to(root).as_posix().encode("utf-8"))
            hasher.update(path.read_bytes())
        else:
            logger.warning("Hash source missing (skipping): %s", path)
    return hasher.hexdigest()[:8]


def update_cache_version(dry_run: bool = False) -> int:
    """Update CACHE_NAME in service-worker.js. Returns exit code."""
    if not SW_FILE.exists():
        logger.error("service-worker.js not found at %s", SW_FILE)
        return 1

    content = SW_FILE.read_text(encoding="utf-8")
    asset_hash = compute_asset_hash()
    new_version = f"v4-{asset_hash}"  # v4+ indicates hash-based versioning

    match = CACHE_NAME_PATTERN.search(content)
    if not match:
        logger.error("Could not find CACHE_NAME pattern in service-worker.js")
        return 1

    current_version = match.group(2)
    if current_version == new_version:
        logger.info("Cache version unchanged: %s", new_version)
        return 0

    new_content = CACHE_NAME_PATTERN.sub(
        rf"\g<1>{new_version}\g<3>",
        content,
        count=1,
    )

    if dry_run:
        logger.info(
            "DRY RUN: would update CACHE_NAME from %r to %r",
            current_version,
            new_version,
        )
        return 0

    SW_FILE.write_text(new_content, encoding="utf-8")
    logger.info("Updated CACHE_NAME: %r → %r", current_version, new_version)
    return 0


def main() -> int:
    """Entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without modifying files",
    )
    args = parser.parse_args()
    return update_cache_version(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
