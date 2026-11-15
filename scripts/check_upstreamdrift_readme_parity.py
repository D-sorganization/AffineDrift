"""Verify UpstreamDrift README at the pinned commit carries the install contract (#5626)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https, require_commit_sha

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "data/upstreamdrift/install_readme_contract.json"
RAW_README = f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{{commit}}/README.md"


def load_contract() -> dict[str, object]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "affinedrift/upstreamdrift-install-readme-contract/v1":
        raise ValueError(f"unexpected contract schema in {CONTRACT_PATH}")
    return payload


def fetch_readme(commit: str) -> str:
    url = RAW_README.format(commit=require_commit_sha(commit))
    try:
        return read_pinned_https(url, host=GITHUB_RAW_HOST).decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch README at {commit}: {exc}") from exc


def readme_requirements(contract: dict[str, object]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    section = contract.get("upstream_readme_requirements")
    if not isinstance(section, dict):
        raise ValueError("contract missing upstream_readme_requirements")
    required = tuple(str(x) for x in section.get("required_substrings", []))
    forbidden = tuple(str(x) for x in section.get("forbidden_substrings", []))
    return required, forbidden


def check_readme(text: str, required: tuple[str, ...], forbidden: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    for needle in required:
        if needle not in text:
            errors.append(f"README missing required substring: {needle!r}")
    for needle in forbidden:
        if needle in text:
            errors.append(f"README contains forbidden substring: {needle!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    contract = load_contract()
    commit = str(contract.get("upstream_readme_commit", ""))
    if len(commit) != 40:
        print("contract upstream_readme_commit must be a 40-character SHA", file=sys.stderr)
        return 1
    required, forbidden = readme_requirements(contract)
    errors = check_readme(fetch_readme(commit), required, forbidden)
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print(f"OK: README at {commit[:12]} matches install parity contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
