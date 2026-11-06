"""Write a verifiable build manifest: commit, Quarto version and lockfile digests (#5319)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "artifacts" / "build-manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    return result.stdout.strip()


def build_manifest(repo_root: Path = ROOT) -> dict[str, str]:
    """Return manifest fields for the current repository tree."""
    quarto = (repo_root / ".quarto-version").read_text(encoding="utf-8").strip()
    return {
        "git_commit": _git_head(repo_root),
        "quarto_version": quarto,
        "python_lock_sha256": _sha256(repo_root / "requirements-docker.lock"),
        "npm_lock_sha256": _sha256(repo_root / "package-lock.json"),
        "generated_at_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat(),
    }


def write_manifest(out_path: Path) -> dict[str, str]:
    """Write manifest JSON to ``out_path`` (creating parents)."""
    payload = build_manifest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output path for build-manifest.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the output file is missing or stale vs current locks",
    )
    args = parser.parse_args(argv)

    if args.check:
        if not args.out.is_file():
            print(f"missing manifest: {args.out}", file=sys.stderr)
            return 1
        on_disk = json.loads(args.out.read_text(encoding="utf-8"))
        current = build_manifest()
        for key in ("git_commit", "python_lock_sha256", "npm_lock_sha256", "quarto_version"):
            if on_disk.get(key) != current[key]:
                print(f"stale manifest field {key}", file=sys.stderr)
                return 1
        return 0

    payload = write_manifest(args.out)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
