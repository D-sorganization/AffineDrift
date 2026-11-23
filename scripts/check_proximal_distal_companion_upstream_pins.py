#!/usr/bin/env python3
"""Fail when lay companion sources link divergent or dead UpstreamDrift paths."""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = ROOT / "data/companion/proximal_distal_companion_upstream_pin.json"
JOURNEY = ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd"
CHAPTERS = ROOT / "articles/proximal_distal_companion/chapters"
LINK_PATTERN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:tree|blob|commit)/([0-9a-fA-F]{7,40})\b"
)
FLOATING = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:tree|blob)/main\b", re.IGNORECASE
)
DEAD_FALSIFICATION = re.compile(r"(?<!MODEL_COMPLETION_)FALSIFICATION_MATRIX\.md")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
PROVIDER = "D-sorganization/UpstreamDrift"


def load_pin(path: Path = PIN_PATH) -> str:
    """Return the canonical 40-character UpstreamDrift commit for companion links."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    commit = payload.get("commit")
    if not isinstance(commit, str) or FULL_SHA.fullmatch(commit) is None:
        raise ValueError(f"invalid companion upstream pin: {path}")
    return commit


def companion_sources() -> list[Path]:
    """Return every lay companion source file subject to the pin gate."""
    paths = [JOURNEY, *sorted(CHAPTERS.glob("ch*.qmd"))]
    return [path for path in paths if path.is_file()]


def _display_path(path: Path) -> str:
    """Return a repo-relative label when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def collect_violations(sources: list[Path], commit: str) -> list[str]:
    """Return human-readable violations for pin drift or floating links."""
    errors: list[str] = []
    for path in sources:
        text = path.read_text(encoding="utf-8")
        label = _display_path(path)
        for match in FLOATING.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{label}:{line}: floating UpstreamDrift/main link")
        for match in DEAD_FALSIFICATION.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{label}:{line}: dead provider path FALSIFICATION_MATRIX.md "
                "(use MODEL_COMPLETION_FALSIFICATION_MATRIX.md)"
            )
        for match in LINK_PATTERN.finditer(text):
            found = match.group(1).lower()
            if len(found) != 40:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{label}:{line}: abbreviated pin {found}")
                continue
            if found != commit:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{label}:{line}: pin {found} != canonical {commit}")
    return errors


def linked_blob_paths(sources: list[Path], commit: str) -> set[str]:
    """Collect unique provider blob paths referenced at the canonical pin."""
    pattern = re.compile(
        rf"github\.com/D-sorganization/UpstreamDrift/blob/{re.escape(commit)}/([^\s\)\]\"]+)"
    )
    paths: set[str] = set()
    for source in sources:
        for match in pattern.finditer(source.read_text(encoding="utf-8")):
            paths.add(match.group(1).rstrip(").,]"))
    return paths


def _gh_api(endpoint: str, *, ref: str | None = None) -> int:
    if ref is not None:
        join = "&" if "?" in endpoint else "?"
        endpoint = f"{endpoint}{join}ref={ref}"
    command = ["gh", "api", endpoint]
    return subprocess.run(command, capture_output=True, text=True, check=False).returncode


def verify_remote(commit: str, blob_paths: set[str]) -> list[str]:
    """Confirm the pin commit and each linked blob exist on GitHub."""
    errors: list[str] = []
    if _gh_api(f"repos/{PROVIDER}/git/commits/{commit}") != 0:
        errors.append(f"UpstreamDrift commit not found: {commit}")
        return errors
    for rel in sorted(blob_paths):
        endpoint = f"repos/{PROVIDER}/contents/{rel}"
        if _gh_api(endpoint, ref=commit) != 0:
            errors.append(f"missing blob at {commit[:12]}: {rel}")
    return errors


def main() -> int:
    """Validate companion UpstreamDrift link pins and optional remote targets."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin-file", type=Path, default=PIN_PATH)
    parser.add_argument(
        "--verify-remotes",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="query GitHub for pin commit and linked blob paths (opt-in; local dev)",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        commit = load_pin(args.pin_file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        LOGGER.error("%s", exc)
        return 1
    sources = companion_sources()
    errors = collect_violations(sources, commit)
    if args.verify_remotes:
        errors.extend(verify_remote(commit, linked_blob_paths(sources, commit)))
    if errors:
        for error in errors:
            LOGGER.error("%s", error)
        return 1
    LOGGER.info(
        "proximal-distal companion pin %s OK (%d blob targets checked)",
        commit[:12],
        len(linked_blob_paths(sources, commit)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
