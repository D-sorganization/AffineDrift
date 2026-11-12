"""Verify AffineDrift install prose matches the UpstreamDrift README contract.

CI gate for AffineDrift #5626: the public install pages must include the README's
mandatory submodule step, the dev editable install, verification, and must not
claim Git LFS is required.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "data/upstreamdrift/install_readme_contract.json"


def load_contract() -> dict[str, object]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "affinedrift/upstreamdrift-install-readme-contract/v1":
        raise ValueError(f"unexpected contract schema in {CONTRACT_PATH}")
    return payload


def check_file(path: Path, required: tuple[str, ...], forbidden: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for needle in required:
        if needle not in text:
            errors.append(f"{path.as_posix()}: missing required substring: {needle!r}")
    for needle in forbidden:
        if needle in text:
            errors.append(f"{path.as_posix()}: forbidden substring present: {needle!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    contract = load_contract()
    file_rules = contract.get("file_requirements")
    if not isinstance(file_rules, dict):
        print("contract missing file_requirements", file=sys.stderr)
        return 1

    errors: list[str] = []
    for rel, rule in sorted(file_rules.items()):
        if not isinstance(rule, dict):
            errors.append(f"invalid rule for {rel}")
            continue
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing monitored file: {rel}")
            continue
        required = tuple(str(x) for x in rule.get("required_substrings", []))
        forbidden = tuple(str(x) for x in rule.get("forbidden_substrings", []))
        errors.extend(check_file(path, required, forbidden))

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print(f"OK: {len(file_rules)} install doc(s) match README contract ({CONTRACT_PATH.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
