"""Reconcile UpstreamDrift implementation bridge includes with the ledger (#5601).

``data/companion/upstream_implementation_links.json`` records which textbook
chapters publish pinned links to implementing UpstreamDrift modules. This gate
fails when a chapter omits its include partial, when partial blob links use a
different commit or path than the ledger, or when a partial link omits a
full 40-character SHA.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "data/companion/upstream_implementation_links.json"
SCHEMA = "affinedrift/upstream-implementation-links/v1"
BLOB_PATTERN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/blob/([0-9a-f]{40})/([^\s\"')]+)"
)
INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+([^>}]+?)\s*>\}\}")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_ledger(path: Path = LEDGER_PATH) -> dict[str, Any]:
    """Load and minimally validate the bridge ledger document."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != SCHEMA:
        raise ValueError(f"unexpected schema_version: {document.get('schema_version')}")
    bridges = document.get("bridges")
    if not isinstance(bridges, list) or not bridges:
        raise ValueError("bridges must be a non-empty list")
    return document


def _normalize_include_token(raw: str) -> str:
    """Strip quotes and whitespace from a Quarto include target."""
    return raw.strip().strip("'\"")


def _chapter_includes(chapter_text: str, include_rel: str) -> bool:
    """Return whether the chapter references the ledger include path."""
    target = include_rel.removeprefix("articles/")
    for match in INCLUDE_PATTERN.finditer(chapter_text):
        token = _normalize_include_token(match.group(1))
        if token.endswith(include_rel.split("articles/", 1)[-1]):
            return True
        if token.endswith(target):
            return True
    return False


def _blob_links(text: str) -> list[tuple[str, str]]:
    return BLOB_PATTERN.findall(text)


def verify_bridge(bridge: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Return human-readable findings for one ledger bridge entry."""
    findings: list[str] = []
    bridge_id = str(bridge.get("id", "?"))
    chapter = root / str(bridge["chapter"])
    include = root / str(bridge["include"])
    commit = str(bridge["commit"])
    paths = list(bridge.get("paths") or [])

    if not FULL_SHA.match(commit):
        findings.append(f"{bridge_id}: commit must be a 40-character SHA")
    if not chapter.is_file():
        findings.append(f"{bridge_id}: missing chapter {bridge['chapter']}")
        return findings
    if not include.is_file():
        findings.append(f"{bridge_id}: missing include {bridge['include']}")
        return findings

    chapter_text = chapter.read_text(encoding="utf-8")
    if not _chapter_includes(chapter_text, str(bridge["include"])):
        findings.append(f"{bridge_id}: chapter does not include {bridge['include']}")

    include_text = include.read_text(encoding="utf-8")
    linked = _blob_links(include_text)
    if not linked:
        findings.append(f"{bridge_id}: include has no pinned UpstreamDrift blob links")

    linked_paths = {path.rstrip("/") for _, path in linked}
    for required in paths:
        normalized = required.rstrip("/")
        if not any(lp == normalized or lp.startswith(f"{normalized}/") for lp in linked_paths):
            findings.append(f"{bridge_id}: include missing blob for {required}")

    for linked_commit, linked_path in linked:
        if linked_commit != commit:
            findings.append(
                f"{bridge_id}: {linked_path} uses commit {linked_commit}, ledger expects {commit}"
            )

    return findings


def verify_document(document: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Verify every bridge entry in the ledger."""
    findings: list[str] = []
    for bridge in document["bridges"]:
        if not isinstance(bridge, dict):
            findings.append("bridge entry must be an object")
            continue
        findings.extend(verify_bridge(bridge, root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--ledger", type=Path, default=None)
    args = parser.parse_args(argv)
    ledger_path = args.ledger or args.root / LEDGER_PATH.relative_to(ROOT)

    try:
        document = load_ledger(ledger_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        write_stderr(str(error))
        return 1

    findings = verify_document(document, args.root)
    if findings:
        for line in findings:
            write_stderr(line)
        return 1

    count = len(document["bridges"])
    write_stdout(f"upstream implementation bridges verified: {count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
