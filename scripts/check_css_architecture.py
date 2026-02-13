#!/usr/bin/env python3
"""Enforce stylesheet architecture boundaries for maintainability."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import load_config, report_results

IMPORT_RE = re.compile(r"""@import\s+(?:url\()?["']([^"']+)["']\)?\s*;""")


def extract_imports(path: Path) -> list[str]:
    """Extract CSS @import specifiers from a stylesheet."""
    text = path.read_text(encoding="utf-8")
    return [match.group(1) for match in IMPORT_RE.finditer(text)]


def check_rules(repo_root: Path) -> list[str]:
    """Validate CSS architecture rules from config."""
    config = load_config(repo_root, "css_architecture_rules.json")
    root_stylesheet = repo_root / config["root_stylesheet"]
    required_imports = set(config["required_root_imports"])
    allowed_prefixes = tuple(config["allowed_root_import_prefixes"])
    feature_glob = config["feature_css_glob"]
    excluded_files = set(config["exclude_feature_css"])

    violations: list[str] = []
    if not root_stylesheet.exists():
        return [f"missing root stylesheet: {config['root_stylesheet']}"]

    root_imports = extract_imports(root_stylesheet)
    root_import_set = set(root_imports)

    missing_required = sorted(required_imports - root_import_set)
    for import_path in missing_required:
        violations.append(f"{config['root_stylesheet']} missing required import: {import_path}")

    for import_path in root_imports:
        if not import_path.startswith(allowed_prefixes):
            violations.append(
                f"{config['root_stylesheet']} has non-modular import '{import_path}' "
                f"(allowed prefixes: {', '.join(allowed_prefixes)})"
            )
            continue
        if not (repo_root / import_path).exists():
            violations.append(f"{config['root_stylesheet']} imports missing file: {import_path}")

    for feature_css in repo_root.glob(feature_glob):
        feature_rel = feature_css.relative_to(repo_root).as_posix()
        if feature_rel in excluded_files:
            continue
        feature_imports = extract_imports(feature_css)
        if feature_imports:
            violations.append(
                f"{feature_rel} must not contain @import (found: {', '.join(feature_imports)})"
            )

    return violations


def main() -> int:
    """Run the CSS architecture check."""
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_rules(repo_root)
    return report_results(
        "CSS architecture check",
        files_scanned=0,
        details=["passed" if not violations else f"{len(violations)} violations"],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
