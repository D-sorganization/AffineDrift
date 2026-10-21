"""Compute an exact Git-index fingerprint for the Quarto render cache."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

_RUNNER = Callable[..., subprocess.CompletedProcess[bytes]]
_KEY_PREFIX = "quarto-render-v3-"
_GIT_TIMEOUT_SECONDS = 15
_OBJECT_ID_RE = re.compile(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
_MODE_RE = re.compile(rb"[0-7]{6}\Z")
_EXCLUDED_PREFIXES = (
    b"tests/",
    b".github/",
    b"docs/development/",
    b"changes/",
)


class CacheKeyError(ValueError):
    """Raised when the index cannot produce a complete render fingerprint."""


def fingerprint_bytes(index_bytes: bytes) -> str:
    """Hash stage-zero Git index records, omitting only known non-render paths."""
    if not isinstance(index_bytes, bytes) or not index_bytes:
        raise CacheKeyError("Git index output must be nonempty bytes")

    if not index_bytes.endswith(b"\0"):
        raise CacheKeyError("Git index output is incomplete")
    records = index_bytes.split(b"\0")[:-1]
    if any(not record for record in records):
        raise CacheKeyError("Git index output contains an empty record")
    retained = [record + b"\0" for record in records if not _excluded_record(record)]
    if not retained:
        raise CacheKeyError("Git index contains no render-relevant files")
    return hashlib.sha256(b"".join(retained)).hexdigest()


def _excluded_record(record: bytes) -> bool:
    path = _record_path(record)
    return path == b"SPEC.md" or path.startswith(_EXCLUDED_PREFIXES)


def _record_path(record: bytes) -> bytes:
    header, separator, path = record.partition(b"\t")
    fields = header.split(b" ")
    if not separator or not path or len(fields) != 3:
        raise CacheKeyError("Git index record is malformed")
    mode, object_id, stage = fields
    if not _MODE_RE.fullmatch(mode) or not _OBJECT_ID_RE.fullmatch(object_id):
        raise CacheKeyError("Git index record metadata is malformed")
    if stage != b"0":
        raise CacheKeyError("Git index has unmerged entries")
    return path


def compute_cache_key(repo_root: Path, *, run: _RUNNER = subprocess.run) -> str:
    """Read the local Git index and return a versioned render cache key."""
    if not repo_root.is_absolute() or not repo_root.is_dir():
        raise CacheKeyError("repository root must be an existing absolute directory")
    try:
        prefix = run(
            ["git", "rev-parse", "--show-prefix"],
            cwd=repo_root,
            capture_output=True,
            text=False,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
        if not isinstance(prefix, subprocess.CompletedProcess) or prefix.returncode != 0:
            raise CacheKeyError("could not locate the repository root")
        if prefix.stdout.rstrip(b"\r\n") != b"":
            raise CacheKeyError("repository root must be the top-level Git directory")
        result = run(
            ["git", "ls-files", "-s", "-z", "--", "."],
            cwd=repo_root,
            capture_output=True,
            text=False,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CacheKeyError("could not read the local Git index") from exc
    if not isinstance(result, subprocess.CompletedProcess) or result.returncode != 0:
        raise CacheKeyError("could not read the local Git index")
    try:
        digest = fingerprint_bytes(result.stdout)
    except CacheKeyError:
        raise
    return f"{_KEY_PREFIX}{digest}"


def _absolute_directory(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError("must name an existing repository directory")
    return path


def main(argv: Sequence[str] | None = None, *, run: _RUNNER = subprocess.run) -> int:
    """Print the exact cache key or fail the workflow step closed."""
    parser = argparse.ArgumentParser(description="Compute the Quarto render cache key.")
    parser.add_argument("--repo-root", type=_absolute_directory, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        key = compute_cache_key(args.repo_root, run=run)
    except CacheKeyError:
        parser.exit(1, "error: could not compute a complete Quarto cache key\n")
    print(key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
