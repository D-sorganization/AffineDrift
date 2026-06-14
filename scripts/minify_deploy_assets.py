#!/usr/bin/env python3
"""Minify deploy-only CSS and JavaScript assets.

Canonical assets stay readable in ``css/`` and ``js/``. This script runs after
Quarto render and mirror checks, shrinking only the generated ``docs/`` files
that are uploaded to GitHub Pages.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from pathlib import Path

CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def minify_css(source: str) -> str:
    """Return a compact CSS string suitable for generated deploy artifacts."""
    text = CSS_COMMENT_RE.sub("", source)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", text)
    text = text.replace(";}", "}")
    return text.strip() + "\n"


def _is_identifier_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "$"}


def minify_js(source: str) -> str:
    """Return JavaScript with comments removed and whitespace collapsed.

    The scanner preserves quoted strings and template literals verbatim. It is
    intentionally conservative: it emits a single space between adjacent
    identifier-like tokens where removing all whitespace could change parsing.
    """
    out: list[str] = []
    i = 0
    pending_space = False
    quote: str | None = None
    escape = False
    previous_emitted = ""

    while i < len(source):
        char = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if quote is not None:
            out.append(char)
            previous_emitted = char
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            i += 1
            continue

        if char in {'"', "'", "`"}:
            if pending_space and previous_emitted and _is_identifier_char(previous_emitted):
                out.append(" ")
            pending_space = False
            quote = char
            out.append(char)
            previous_emitted = char
            i += 1
            continue

        if char == "/" and nxt == "/":
            i += 2
            while i < len(source) and source[i] not in "\r\n":
                i += 1
            pending_space = True
            continue

        if char == "/" and nxt == "*":
            i += 2
            while i + 1 < len(source) and not (source[i] == "*" and source[i + 1] == "/"):
                i += 1
            i += 2
            pending_space = True
            continue

        if char.isspace():
            pending_space = True
            i += 1
            continue

        if (
            pending_space
            and previous_emitted
            and _is_identifier_char(previous_emitted)
            and _is_identifier_char(char)
        ):
            out.append(" ")
        pending_space = False
        out.append(char)
        previous_emitted = char
        i += 1

    return "".join(out).strip() + "\n"


def minify_file(path: Path, minifier: Callable[[str], str]) -> None:
    path.write_text(minifier(path.read_text(encoding="utf-8")), encoding="utf-8")


def minify_deploy_assets(repo_root: Path) -> list[Path]:
    """Minify generated deploy assets and return the files touched."""
    touched: list[Path] = []
    css_path = repo_root / "docs" / "styles.css"
    if css_path.is_file():
        minify_file(css_path, minify_css)
        touched.append(css_path)

    js_dir = repo_root / "docs" / "js"
    if js_dir.is_dir():
        for js_path in sorted(js_dir.glob("*.js")):
            minify_file(js_path, minify_js)
            touched.append(js_path)
    return touched


def main() -> int:
    parser = argparse.ArgumentParser(description="Minify generated docs CSS/JS deploy assets")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root containing docs/",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    touched = minify_deploy_assets(repo_root)
    for path in touched:
        print(f"minified {path.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
