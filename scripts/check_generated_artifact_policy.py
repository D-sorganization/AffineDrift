#!/usr/bin/env python3
"""Enforce generated-artifact governance for source-quality checks."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.utils.budget_check_utils import (  # noqa: E402 -- reason: repo root must be added before local imports
    load_config,
    report_results,
)


@dataclass(frozen=True)
class GeneratedArtifactPolicy:
    """Generated roots and source-quality roots that must not overlap."""

    generated_roots: tuple[str, ...]
    source_quality_include_roots: tuple[str, ...]


def _normalize_root(path: str) -> str:
    """Normalize a repo-relative root to POSIX form with a trailing slash."""
    normalized = path.replace("\\", "/").strip("/")
    return f"{normalized}/" if normalized else ""


def load_policy(repo_root: Path) -> GeneratedArtifactPolicy:
    """Load generated-artifact policy from ``config/generated_artifact_policy.json``."""
    raw = load_config(repo_root, "generated_artifact_policy.json")
    return GeneratedArtifactPolicy(
        generated_roots=tuple(_normalize_root(item) for item in raw["generated_roots"]),
        source_quality_include_roots=tuple(
            _normalize_root(item) for item in raw["source_quality_include_roots"]
        ),
    )


def validate_policy(repo_root: Path, policy: GeneratedArtifactPolicy) -> list[str]:
    """Return policy errors for generated roots that leak into source-quality budgets."""
    errors: list[str] = []
    gitignore_text = (repo_root / ".gitignore").read_text(encoding="utf-8")
    source_quality_roots = {_normalize_root(item) for item in policy.source_quality_include_roots}
    for generated_root in (_normalize_root(item) for item in policy.generated_roots):
        if generated_root in source_quality_roots:
            errors.append(
                f"generated root {generated_root} must not be in source-quality include roots"
            )
        ignore_entry = f"/{generated_root}"
        if ignore_entry not in gitignore_text:
            errors.append(f"generated root {generated_root} must be ignored via {ignore_entry}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for generated-artifact policy validation."""
    args = list(argv or [])
    repo_root = Path(args[0]) if args else Path.cwd()
    policy = load_policy(repo_root)
    errors = validate_policy(repo_root, policy)
    details = [
        "generated roots: " + ", ".join(policy.generated_roots),
        "source-quality roots: " + ", ".join(policy.source_quality_include_roots),
    ]
    return report_results("Generated artifact policy check", 1, details=details, errors=errors)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
