"""UpstreamDrift implementation bridge ledger verification (#5601).

The ledger in ``data/companion/upstream_implementation_links.json`` backs PoG and GoM
chapter includes under ``articles/_includes/upstream-implementation/``.
"""

from __future__ import annotations

import json
import re
import urllib.error
from collections.abc import Callable
from pathlib import Path
from typing import Any

from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https, require_commit_sha

SCHEMA = "affinedrift/upstream-implementation-links/v1"
BLOB_PATTERN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/blob/([0-9a-f]{40})/([^\s\"')]+)"
)
INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+([^>}]+?)\s*>\}\}")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_ledger(path: Path) -> dict[str, Any]:
    """Load and minimally validate the bridge ledger document."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != SCHEMA:
        raise ValueError(f"unexpected schema_version: {document.get('schema_version')}")
    bridges = document.get("bridges")
    if not isinstance(bridges, list) or not bridges:
        raise ValueError("bridges must be a non-empty list")
    return document


def _normalize_include_token(raw: str) -> str:
    """Strip whitespace and optional quotes from a Quarto include token."""
    return raw.strip().strip("'\"")


def _chapter_includes(chapter_text: str, include_rel: str) -> bool:
    """Return whether the chapter references the ledger include path."""
    target = include_rel.removeprefix("articles/")
    tail = include_rel.split("articles/", 1)[-1]
    for match in INCLUDE_PATTERN.finditer(chapter_text):
        token = _normalize_include_token(match.group(1))
        if token.endswith(tail) or token.endswith(target):
            return True
    return False


def _blob_links(text: str) -> list[tuple[str, str]]:
    """Extract pinned UpstreamDrift blob URLs as (commit, path) pairs."""
    return BLOB_PATTERN.findall(text)


def verify_bridge(bridge: dict[str, Any], root: Path) -> list[str]:
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


def verify_document(document: dict[str, Any], root: Path) -> list[str]:
    """Verify every bridge entry in the ledger."""
    findings: list[str] = []
    for bridge in document["bridges"]:
        if not isinstance(bridge, dict):
            findings.append("bridge entry must be an object")
            continue
        findings.extend(verify_bridge(bridge, root))
    return findings


FetchPath = Callable[[str, str], None]


def _default_fetch_path(commit: str, path: str) -> None:
    """Fetch one pinned UpstreamDrift path to prove it exists at ``commit``."""
    require_commit_sha(commit)
    normalized = path.lstrip("/")
    url = f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{commit}/{normalized}"
    read_pinned_https(url, host=GITHUB_RAW_HOST)


def verify_remote_paths(
    document: dict[str, Any],
    *,
    fetch_path: FetchPath | None = None,
) -> list[str]:
    """Verify ledger paths exist at their pinned commits on raw.githubusercontent.com."""
    fetch = fetch_path or _default_fetch_path
    findings: list[str] = []
    seen: set[tuple[str, str]] = set()
    for bridge in document["bridges"]:
        if not isinstance(bridge, dict):
            continue
        bridge_id = str(bridge.get("id", "?"))
        commit = str(bridge.get("commit", ""))
        if not FULL_SHA.match(commit):
            findings.append(f"{bridge_id}: commit must be a 40-character SHA for remote check")
            continue
        for raw_path in bridge.get("paths") or []:
            path = str(raw_path).rstrip("/")
            key = (commit, path)
            if key in seen:
                continue
            seen.add(key)
            try:
                fetch(commit, path)
            except (OSError, ValueError, urllib.error.URLError) as error:
                findings.append(f"{bridge_id}: missing remote path {path} at {commit[:8]} ({error})")
    return findings
