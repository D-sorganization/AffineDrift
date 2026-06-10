#!/usr/bin/env python3
"""Flatten the render-blocking ``@import`` chain in ``styles.css`` into a bundle.

``styles.css`` is authored as a modular ``@import`` graph (19 direct imports,
one of which pulls in 9 nested token files). Browsers cannot fetch a level-2
import until the level-1 stylesheet has downloaded and parsed, serializing ~26
small CSS requests on the critical rendering path (issue #3219).

This tool recursively inlines every same-tree ``@import`` into a single
flattened ``docs/styles.css`` **build artifact**. The canonical ``styles.css``
and ``css/`` sources stay modular for authoring; only the served copy is
flattened.

Pure ``bundle()`` is unit-tested in ``tests/test_css_bundle.py``.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Matches both `@import "x.css";` and `@import url("x.css");` (and url(...) with
# single quotes). Captures the target path.
IMPORT_RE = re.compile(
    r"""@import\s+(?:url\(\s*)?["']([^"']+)["']\s*\)?\s*;""",
)


def _strip_remote(target: str) -> str | None:
    """Return None for imports we should leave as-is (remote / data URIs)."""
    if target.startswith(("http://", "https://", "//", "data:")):
        return None
    # Strip any media-query/url fragment query string for resolution purposes.
    return target.split("?", 1)[0].split("#", 1)[0]


def bundle(entry: Path, root: Path, _seen: set[Path] | None = None) -> str:
    """Recursively inline ``@import`` statements starting at ``entry``.

    Parameters
    ----------
    entry:
        Path to the stylesheet to inline (absolute or relative to cwd).
    root:
        Repository root; relative imports are resolved against the importing
        file's directory, never escaping the tree.
    _seen:
        Internal cycle guard.

    Returns
    -------
    str
        The flattened stylesheet text with zero local ``@import`` statements.
    """
    seen = _seen if _seen is not None else set()
    entry = entry.resolve()
    if entry in seen:
        # Cycle / diamond import — emit nothing the second time.
        return ""
    seen.add(entry)

    text = entry.read_text(encoding="utf-8")
    out_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        match = IMPORT_RE.search(line)
        if match is None:
            out_lines.append(line)
            continue

        target = _strip_remote(match.group(1))
        if target is None:
            # Remote import: keep it verbatim (cannot be inlined).
            out_lines.append(line)
            continue

        child = (entry.parent / target).resolve()
        if not child.exists():
            # Unknown local import: keep the original line so nothing silently
            # disappears (and CI/render will surface a genuine missing file).
            out_lines.append(line)
            continue

        inlined = bundle(child, root, seen)
        out_lines.append(f"/* --- inlined: {target} --- */\n")
        out_lines.append(inlined)
        if not inlined.endswith("\n"):
            out_lines.append("\n")

    return "".join(out_lines)


def build_bundle(root: Path, entry_rel: str = "styles.css") -> str:
    """Build the flattened bundle text for the site entry stylesheet."""
    return bundle(root / entry_rel, root)


def main(argv: list[str] | None = None) -> None:
    """CLI: write the flattened bundle to ``--output`` (default docs/styles.css)."""
    parser = argparse.ArgumentParser(description="Flatten styles.css @import chain")
    parser.add_argument("--entry", default="styles.css", help="Entry stylesheet (relative to root)")
    parser.add_argument(
        "--output",
        default="docs/styles.css",
        help="Where to write the flattened bundle.",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    bundled = build_bundle(root, args.entry)
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(bundled, encoding="utf-8")


if __name__ == "__main__":
    main()
