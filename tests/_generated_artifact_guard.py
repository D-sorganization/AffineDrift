"""Detect test runs that rewrite committed generated artifacts.

Tests must be hermetic: a generator exercised by a test has to write into
``tmp_path`` (or run in ``check`` mode), never over the committed copies. The
session hooks in ``tests/conftest.py`` snapshot these directories before the
run and fail the session if any file was modified, created, or deleted.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

GUARDED_DIRS = ("data/trust/generated", "_includes/generated")


def snapshot_generated_artifacts(
    root: Path, guarded_dirs: tuple[str, ...] = GUARDED_DIRS
) -> dict[str, str]:
    """Return ``{repo-relative posix path: sha256}`` for every guarded file."""
    snapshot: dict[str, str] = {}
    for relative in guarded_dirs:
        base = root / relative
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                snapshot[path.relative_to(root).as_posix()] = digest
    return snapshot


def changed_generated_artifacts(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """Describe every path that was modified, created, or deleted."""
    changes = [
        f"modified: {p}" for p in sorted(before.keys() & after.keys()) if before[p] != after[p]
    ]
    changes += [f"created: {p}" for p in sorted(after.keys() - before.keys())]
    changes += [f"deleted: {p}" for p in sorted(before.keys() - after.keys())]
    return changes
