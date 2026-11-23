"""Governed UpstreamDrift permalinks in AffineDrift articles (#5601)."""

from __future__ import annotations

import json
import re
import urllib.error
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https, require_commit_sha

SCHEMA = "affinedrift/upstream-article-link-pins/v1"
FLOATING_MAIN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:tree|blob)/main\b", re.IGNORECASE
)
LINK_PATTERN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:tree|blob|commit)/([0-9a-fA-F]{7,40})\b"
)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SCAN_SUFFIXES = (".qmd", ".md")


def load_contract(path: Path) -> dict[str, Any]:
    """Load and validate the article link pin contract."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != SCHEMA:
        raise ValueError(f"unexpected schema_version: {document.get('schema_version')}")
    governed = document.get("governed_sources")
    if not isinstance(governed, list) or not governed:
        raise ValueError("governed_sources must be a non-empty list")
    return document


def _iter_scan_files(root: Path, scan_roots: Sequence[str]) -> Iterable[Path]:
    """Yield Markdown and Quarto sources under each configured scan root."""
    for rel in scan_roots:
        base = root / rel
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.suffix in SCAN_SUFFIXES and path.is_file():
                yield path


def _line_number(text: str, index: int) -> int:
    """Return the 1-based line number for a character offset in ``text``."""
    return text.count("\n", 0, index) + 1


def find_floating_main_links(root: Path, scan_roots: Sequence[str]) -> list[str]:
    """Return violations for UpstreamDrift links that use the moving ``main`` ref."""
    findings: list[str] = []
    for path in _iter_scan_files(root, scan_roots):
        text = path.read_text(encoding="utf-8")
        label = str(path.relative_to(root))
        for match in FLOATING_MAIN.finditer(text):
            line = _line_number(text, match.start())
            findings.append(f"{label}:{line}: floating UpstreamDrift/main link")
    return findings


def verify_governed_source(root: Path, entry: dict[str, Any]) -> list[str]:
    """Check one governed article for floating ``main`` refs and abbreviated SHAs."""
    findings: list[str] = []
    rel = str(entry["path"])
    path = root / rel
    source_id = str(entry.get("id", rel))
    if not path.is_file():
        findings.append(f"{source_id}: missing governed source {rel}")
        return findings

    text = path.read_text(encoding="utf-8")
    for match in FLOATING_MAIN.finditer(text):
        line = _line_number(text, match.start())
        findings.append(f"{rel}:{line}: floating UpstreamDrift/main link")
    for match in LINK_PATTERN.finditer(text):
        found = match.group(1).lower()
        line = _line_number(text, match.start())
        if len(found) != 40:
            findings.append(f"{rel}:{line}: abbreviated UpstreamDrift pin {found}")
    return findings


def verify_contract(document: dict[str, Any], root: Path) -> list[str]:
    """Verify floating-main scan and every governed source entry."""
    findings: list[str] = []
    scan_roots = list(document.get("floating_main_scan_roots") or ["articles"])
    findings.extend(find_floating_main_links(root, scan_roots))
    for entry in document["governed_sources"]:
        findings.extend(verify_governed_source(root, entry))
    return findings


def _raw_url(commit: str, repo_path: str) -> str:
    """Build a pinned raw.githubusercontent.com URL for an UpstreamDrift path."""
    commit = require_commit_sha(commit)
    return f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{commit}/{repo_path}"


def verify_remote_paths(
    document: dict[str, Any],
    fetch_path: Callable[[str, str], None] | None = None,
) -> list[str]:
    """HEAD each ``remote_paths`` entry via raw.githubusercontent.com."""
    findings: list[str] = []
    fetcher = fetch_path or _default_fetch

    for entry in document["governed_sources"]:
        source_id = str(entry.get("id", entry.get("path", "?")))
        for item in entry.get("remote_paths") or []:
            commit = str(item["commit"])
            repo_path = str(item["path"]).lstrip("/")
            try:
                require_commit_sha(commit)
            except ValueError as error:
                findings.append(f"{source_id}: {error}")
                continue
            try:
                fetcher(commit, repo_path)
            except FileNotFoundError:
                findings.append(f"{source_id}: missing remote path {repo_path} at {commit}")
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    findings.append(f"{source_id}: missing remote path {repo_path} at {commit}")
                else:
                    findings.append(f"{source_id}: HTTP {error.code} for {repo_path} at {commit}")
            except OSError as error:
                findings.append(f"{source_id}: failed to fetch {repo_path}: {error}")
    return findings


def _default_fetch(commit: str, repo_path: str) -> None:
    """Fetch one pinned UpstreamDrift object; raise when the path is missing."""
    url = _raw_url(commit, repo_path)
    read_pinned_https(url, host=GITHUB_RAW_HOST, timeout=60.0)
