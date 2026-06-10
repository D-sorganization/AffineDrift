#!/usr/bin/env python3
"""Flatten the canonical CSS ``@import`` graph into a single bundle (issue #3219).

``styles.css`` is authored as a modular, 3-level-deep ``@import`` waterfall (26
small render-blocking requests). The canonical sources under ``css/`` stay
modular for authoring and for ``check_css_architecture.py``; this build step
recursively inlines every ``@import`` into one flattened ``docs/styles.css`` so
production browsers fetch a single stylesheet on the critical rendering path.

Resolution rules
----------------
- ``@import`` specifiers are resolved relative to the *importing* file's
  directory (so a nested ``@import url("colors.css")`` inside
  ``css/tokens/design-tokens.css`` resolves to ``css/tokens/colors.css``).
- Each file is inlined at most once (guards against duplicate/cyclic imports).
- Output is deterministic for a given source tree.

Usage::

    python3 scripts/bundle_css.py                      # writes docs/styles.css
    python3 scripts/bundle_css.py --check              # fail if docs/ is stale
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

IMPORT_RE = re.compile(r"""@import\s+(?:url\()?["']([^"']+)["']\)?\s*;""")


def extract_imports(css_text: str) -> list[str]:
    """Return the ordered list of ``@import`` specifiers in a stylesheet."""
    return IMPORT_RE.findall(css_text)


def _resolve(spec: str, importer: Path, repo_root: Path) -> Path:
    """Resolve an import specifier relative to the importing file's directory."""
    candidate = (importer.parent / spec).resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"{importer.relative_to(repo_root)} imports missing file: {spec}")
    return candidate


def collect_import_graph(entry: Path, repo_root: Path) -> list[Path]:
    """Return all files reachable from ``entry`` via ``@import`` (excluding entry).

    Order is a stable depth-first pre-order traversal, each file listed once.
    """
    seen: set[Path] = set()
    graph: list[Path] = []

    def walk(path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        for spec in extract_imports(text):
            resolved = _resolve(spec, path, repo_root)
            if resolved in seen:
                continue
            seen.add(resolved)
            graph.append(resolved)
            walk(resolved)

    walk(entry)
    return graph


def _inline(path: Path, repo_root: Path, seen: set[Path]) -> str:
    """Recursively inline a stylesheet, replacing each ``@import`` with content."""
    text = path.read_text(encoding="utf-8")
    out_lines: list[str] = []
    rel = path.relative_to(repo_root).as_posix()
    out_lines.append(f"/* ===== begin {rel} ===== */")
    for line in text.splitlines():
        match = IMPORT_RE.search(line)
        if match:
            resolved = _resolve(match.group(1), path, repo_root)
            if resolved in seen:
                continue
            seen.add(resolved)
            out_lines.append(_inline(resolved, repo_root, seen))
            continue
        out_lines.append(line)
    out_lines.append(f"/* ===== end {rel} ===== */")
    return "\n".join(out_lines)


def bundle(entry: Path, repo_root: Path) -> str:
    """Return the flattened, import-free bundle for ``entry``."""
    seen: set[Path] = set()
    result = _inline(entry, repo_root, seen)
    if not result.endswith("\n"):
        result += "\n"
    return result


def main() -> int:
    """Build the bundle and write/verify ``docs/styles.css``."""
    parser = argparse.ArgumentParser(description="Flatten CSS @import graph into a bundle")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify docs/styles.css matches a freshly computed bundle; exit 1 on drift",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    entry = repo_root / "styles.css"
    output = repo_root / "docs" / "styles.css"

    flattened = bundle(entry, repo_root)

    if args.check:
        if not output.exists():
            print(f"MISSING BUNDLE: {output.relative_to(repo_root)}", file=sys.stderr)
            return 1
        current = output.read_text(encoding="utf-8")
        if current != flattened:
            print(
                "DRIFT: docs/styles.css is stale; run scripts/bundle_css.py",
                file=sys.stderr,
            )
            return 1
        print("docs/styles.css bundle is up to date.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(flattened, encoding="utf-8")
    print(
        f"Wrote bundle: {output.relative_to(repo_root)} "
        f"({len(collect_import_graph(entry, repo_root))} files inlined, 0 @imports)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
