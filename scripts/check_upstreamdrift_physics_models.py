"""Verify UpstreamDrift physics inventory pin and site copy against live source (#5624)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path
from typing import Any, cast

from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https, require_commit_sha

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "data" / "upstreamdrift" / "physics_models_contract.json"
RAW_SOURCE = f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{{commit}}/{{path}}"


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"contract in {path} must be a JSON object")
    schema = payload.get("schema_version")
    if schema != "affinedrift/upstreamdrift-physics-models-contract/v1":
        raise ValueError(f"unexpected contract schema in {path}: {schema!r}")
    return cast(dict[str, Any], payload)


def fetch_upstream_file(commit: str, relative_path: str) -> str:
    url = RAW_SOURCE.format(
        commit=require_commit_sha(commit),
        path=relative_path.lstrip("/"),
    )
    try:
        return read_pinned_https(url, host=GITHUB_RAW_HOST).decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch {relative_path} at {commit[:12]}: {exc}") from exc


def check_substrings(
    label: str,
    text: str,
    required: tuple[str, ...],
    forbidden: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    for needle in required:
        if needle not in text:
            errors.append(f"{label} missing required substring: {needle!r}")
    for needle in forbidden:
        if needle in text:
            errors.append(f"{label} contains forbidden substring: {needle!r}")
    return errors


def check_upstream_sources(contract: dict[str, Any]) -> list[str]:
    commit = str(contract.get("upstream_commit", ""))
    if len(commit) != 40:
        return ["contract upstream_commit must be a 40-character SHA"]
    errors: list[str] = []
    checks = contract.get("upstream_source_checks", [])
    if not isinstance(checks, list):
        return ["contract missing upstream_source_checks list"]
    for entry in checks:
        if not isinstance(entry, dict):
            errors.append("upstream_source_checks entry is not an object")
            continue
        check_id = str(entry.get("id", "?"))
        path = str(entry.get("path", ""))
        if not path:
            errors.append(f"{check_id}: missing path")
            continue
        required = tuple(str(x) for x in entry.get("required_substrings", []))
        forbidden = tuple(str(x) for x in entry.get("forbidden_substrings", []))
        try:
            text = fetch_upstream_file(commit, path)
        except RuntimeError as exc:
            errors.append(f"{check_id}: {exc}")
            continue
        errors.extend(
            check_substrings(f"UpstreamDrift {path} ({check_id})", text, required, forbidden)
        )
    return errors


def check_site_files(contract: dict[str, Any], repo_root: Path = ROOT) -> list[str]:
    checks = contract.get("site_file_checks", [])
    if not isinstance(checks, list):
        return ["contract missing site_file_checks list"]
    errors: list[str] = []
    for entry in checks:
        if not isinstance(entry, dict):
            errors.append("site_file_checks entry is not an object")
            continue
        rel_path = str(entry.get("path", ""))
        if not rel_path:
            errors.append("site_file_checks entry missing path")
            continue
        file_path = repo_root / rel_path
        if not file_path.is_file():
            errors.append(f"site file missing: {rel_path}")
            continue
        text = file_path.read_text(encoding="utf-8")
        required = tuple(str(x) for x in entry.get("required_substrings", []))
        forbidden = tuple(str(x) for x in entry.get("forbidden_substrings", []))
        errors.extend(check_substrings(rel_path, text, required, forbidden))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        contract = load_contract()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"contract load failed: {exc}", file=sys.stderr)
        return 1
    errors = check_site_files(contract) + check_upstream_sources(contract)
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    commit = str(contract["upstream_commit"])
    print(f"OK: physics inventory matches UpstreamDrift {commit[:12]} and site files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
