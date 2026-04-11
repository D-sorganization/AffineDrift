#!/usr/bin/env python3
"""Function size gate - fails CI if any function exceeds the LOC threshold.

Fixes #2368 and #2362: enforce maximum function size to prevent god-functions.

Usage:
    python scripts/check_function_size.py [--threshold 40] [--src src]
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import sys


def get_function_sizes(path: pathlib.Path) -> list[tuple[str, int, int]]:
    """Return (func_name, start_line, size) for all functions in a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            size = (node.end_lineno or node.lineno) - node.lineno + 1
            results.append((node.name, node.lineno, size))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Function size gate")
    parser.add_argument("--threshold", type=int, default=40, help="Max lines per function")
    parser.add_argument("--warn", type=int, default=25, help="Warning threshold")
    parser.add_argument("--src", default="src", help="Source directory")
    args = parser.parse_args()

    src_dir = pathlib.Path(args.src)
    if not src_dir.exists():
        print(f"Source dir not found: {src_dir}", file=sys.stderr)
        return 0  # Non-fatal if src doesn't exist

    failures: list[tuple[pathlib.Path, str, int, int]] = []
    warnings: list[tuple[pathlib.Path, str, int, int]] = []

    for pyfile in sorted(src_dir.rglob("*.py")):
        if "__pycache__" in str(pyfile):
            continue
        for fname, lineno, size in get_function_sizes(pyfile):
            if size >= args.threshold:
                failures.append((pyfile, fname, lineno, size))
            elif size >= args.warn:
                warnings.append((pyfile, fname, lineno, size))

    if warnings:
        print(f"WARN: {len(warnings)} functions approaching size threshold ({args.warn} lines):")
        for f, fn, ln, sz in sorted(warnings, key=lambda x: -x[3])[:10]:
            print(f"  {sz:3d} lines  {f}:{ln}  {fn}()")

    if failures:
        print(
            f"\nFAIL: {len(failures)} functions exceed {args.threshold} lines (fixes #2362/#2368):"
        )
        for f, fn, ln, sz in sorted(failures, key=lambda x: -x[3])[:20]:
            print(f"  {sz:3d} lines  {f}:{ln}  {fn}()")
        print("\nDecompose these functions into smaller units.")
        return 1

    total = sum(1 for _ in src_dir.rglob("*.py"))
    print(f"OK: No oversized functions (>{args.threshold} lines) in {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
