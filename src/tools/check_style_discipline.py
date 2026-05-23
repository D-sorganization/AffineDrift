#!/usr/bin/env python3
"""Lint QMD files for inline styles, gradients, and hardcoded hex (issue #3140 E2)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

INLINE_STYLE_RE = re.compile(r'\sstyle=["\']')
GRADIENT_RE = re.compile(r"linear-gradient\(|radial-gradient\(")
HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}(?![0-9a-fA-F])")

EXCLUDED_DIRS = {"articles", "site_libs", "docs", ".git", "node_modules"}


def check_file(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"Expected file: {path}")
    violations: list[str] = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if INLINE_STYLE_RE.search(line):
            violations.append(f"{path}:{lineno}: inline style= attribute")
        if GRADIENT_RE.search(line):
            violations.append(f"{path}:{lineno}: gradient function")
        if HEX_COLOR_RE.search(line):
            violations.append(f"{path}:{lineno}: hardcoded hex color")
    return violations


def main() -> int:
    root = Path(__file__).parent.parent.parent
    qmd_files = [
        p for p in root.rglob("*.qmd") if not any(part in EXCLUDED_DIRS for part in p.parts)
    ]
    all_violations: list[str] = []
    for qmd in sorted(qmd_files):
        all_violations.extend(check_file(qmd))
    if all_violations:
        for v in all_violations:
            print(v)
        return 1
    print(f"Checked {len(qmd_files)} QMD files — no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
