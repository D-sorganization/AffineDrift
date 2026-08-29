#!/usr/bin/env python3
"""Enforce stylesheet architecture boundaries for maintainability."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils.budget_check_utils import load_config, report_results

IMPORT_RE = re.compile(r"""@import\s+(?:url\()?["']([^"']+)["']\)?\s*;""")

# A media-query prelude runs from `@media` up to the opening `{`. CSS custom
# properties (var(...)) are NOT valid there — such a query parses as `not all`
# and is silently dropped by every browser (issue #3326). Match `@media ... var(`
# before the first `{` on a logical line, ignoring CSS comment bodies.
MEDIA_VAR_RE = re.compile(r"@media[^{]*\bvar\(")
# Strip `/* ... */` block comments so doc-comment examples don't trip the check.
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def extract_imports(path: Path) -> list[str]:
    """Extract CSS @import specifiers from a stylesheet."""
    text = path.read_text(encoding="utf-8")
    return [match.group(1) for match in IMPORT_RE.finditer(text)]


def discover_authored_stylesheets(repo_root: Path, root_stylesheet: Path) -> list[Path]:
    """Return every canonical authored stylesheet in deterministic order.

    The root entry point is reported first, followed by the modular ``css/``
    tree.  An empty result is a broken gate, not a passing scan.
    """
    discovered: list[Path] = []
    if root_stylesheet.is_file():
        discovered.append(root_stylesheet)
    discovered.extend(sorted(repo_root.glob("css/**/*.css")))
    unique = list(dict.fromkeys(discovered))
    if not unique:
        raise ValueError(f"no authored stylesheets discovered under {repo_root}")
    return unique


def find_media_var_violations(path: Path, repo_root: Path) -> list[str]:
    """Return violations for ``var()`` used inside a ``@media`` prelude.

    CSS variables are invalid in media-query preludes; the rule is dropped, so
    responsive layout silently breaks (issue #3326). Comment bodies are ignored
    so the canonical token files may document the px-literal convention.
    """
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(repo_root).as_posix()
    violations: list[str] = []
    # Blank out comments while preserving newlines so line numbers stay accurate.
    decommented = COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    for lineno, line in enumerate(decommented.splitlines(), start=1):
        if MEDIA_VAR_RE.search(line):
            violations.append(
                f"{rel}:{lineno} uses var() inside a @media prelude "
                f"(invalid CSS, dropped by browsers; use literal px — #3326)"
            )
    return violations


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

    # Forbid var() inside @media preludes across every authored stylesheet
    # (root entry + the modular css/ tree). The rendered docs/ bundle inherits
    # correctness from these sources via scripts/bundle_css.py.
    media_var_targets = discover_authored_stylesheets(repo_root, root_stylesheet)
    for css_file in media_var_targets:
        violations.extend(find_media_var_violations(css_file, repo_root))

    return violations


def main() -> int:
    """Run the CSS architecture check."""
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_rules(repo_root)
    root_stylesheet = (
        repo_root / load_config(repo_root, "css_architecture_rules.json")["root_stylesheet"]
    )
    try:
        files_scanned = len(discover_authored_stylesheets(repo_root, root_stylesheet))
    except ValueError:
        files_scanned = 0
    return report_results(
        "CSS architecture check",
        files_scanned=files_scanned,
        details=["passed" if not violations else f"{len(violations)} violations"],
        errors=violations,
    )


if __name__ == "__main__":
    sys.exit(main())
