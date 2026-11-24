#!/usr/bin/env python3
"""Fail when learning-path or resources pages regress #5618 citation fixes."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = Path("config/learning_path_resource_contract.yml")


@dataclass(frozen=True)
class ContractRule:
    """Per-file forbidden and required substring rules."""

    path: Path
    forbidden: tuple[str, ...]
    required: tuple[str, ...]


@dataclass(frozen=True)
class GlobalRule:
    """Forbidden substrings applied to files matching glob patterns."""

    globs: tuple[str, ...]
    forbidden: tuple[str, ...]


@dataclass(frozen=True)
class ResourceContract:
    """Loaded contract from YAML."""

    file_rules: tuple[ContractRule, ...]
    global_rules: tuple[GlobalRule, ...]


@dataclass(frozen=True)
class Violation:
    """A single contract failure."""

    path: Path
    kind: str
    detail: str


def _as_string_tuple(values: Any, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(values)


def load_contract(config_path: Path) -> ResourceContract:
    """Load regression contracts from YAML."""
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Expected mapping in {config_path}")

    file_rules: list[ContractRule] = []
    for entry in raw.get("file_rules") or []:
        if not isinstance(entry, dict) or "path" not in entry:
            raise ValueError(f"Invalid file_rules entry in {config_path}: {entry!r}")
        file_rules.append(
            ContractRule(
                path=Path(entry["path"]),
                forbidden=_as_string_tuple(entry.get("forbidden"), "forbidden"),
                required=_as_string_tuple(entry.get("required"), "required"),
            )
        )

    global_rules: list[GlobalRule] = []
    for entry in raw.get("global_rules") or []:
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid global_rules entry in {config_path}: {entry!r}")
        global_rules.append(
            GlobalRule(
                globs=_as_string_tuple(entry.get("globs"), "globs"),
                forbidden=_as_string_tuple(entry.get("forbidden"), "forbidden"),
            )
        )

    return ResourceContract(
        file_rules=tuple(file_rules),
        global_rules=tuple(global_rules),
    )


def _check_text(
    rel_path: Path, text: str, forbidden: tuple[str, ...], required: tuple[str, ...]
) -> list[Violation]:
    violations: list[Violation] = []
    for needle in forbidden:
        if needle in text:
            violations.append(
                Violation(path=rel_path, kind="forbidden", detail=f"forbidden substring {needle!r}")
            )
    for needle in required:
        if needle not in text:
            violations.append(
                Violation(
                    path=rel_path, kind="missing_required", detail=f"missing required {needle!r}"
                )
            )
    return violations


def check_contract(
    repo_root: Path,
    file_rules: tuple[ContractRule, ...],
    global_rules: tuple[GlobalRule, ...],
) -> list[Violation]:
    """Evaluate all contract rules under *repo_root*."""
    violations: list[Violation] = []
    for rule in file_rules:
        target = repo_root / rule.path
        if not target.exists():
            violations.append(
                Violation(path=rule.path, kind="missing_file", detail="contracted file not found")
            )
            continue
        text = target.read_text(encoding="utf-8")
        violations.extend(_check_text(rule.path, text, rule.forbidden, rule.required))

    for global_rule in global_rules:
        matched_paths: set[Path] = set()
        for pattern in global_rule.globs:
            for match in repo_root.glob(pattern):
                if match.is_file():
                    matched_paths.add(match.relative_to(repo_root))
        for rel_path in sorted(matched_paths):
            text = (repo_root / rel_path).read_text(encoding="utf-8")
            violations.extend(_check_text(rel_path, text, global_rule.forbidden, ()))
    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry."""
    parser = argparse.ArgumentParser(
        description="Verify learning-path and resources citation contracts (#5618)."
    )
    parser.add_argument("repo_root", nargs="?", default=".", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    config_path = args.config if args.config.is_absolute() else repo_root / args.config
    contract = load_contract(config_path)
    violations = check_contract(repo_root, contract.file_rules, contract.global_rules)

    if not violations:
        print(
            "learning-path resources: OK — "
            f"{len(contract.file_rules)} file rule(s), "
            f"{len(contract.global_rules)} global rule(s)"
        )
        return 0

    for violation in violations:
        print(f"{violation.path}: {violation.kind} — {violation.detail}")
    print(f"\nlearning-path resources: {len(violations)} violation(s)")
    return 1


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(sys.argv[1:]))
