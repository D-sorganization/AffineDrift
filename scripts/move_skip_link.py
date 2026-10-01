"""Quarto post-render step: make the static skip link the first child of ``<body>``.

Quarto's website layout places ``include-before-body`` content inside ``<main>``,
after the navbar, so the skip link from ``_includes/skip-link.html`` would come
after every navbar link in the Tab order (issue #4566). This step moves that one
link to directly after the ``<body>`` tag in each rendered page, so it is the
first focusable element without any JavaScript.

Quarto runs it with ``QUARTO_PROJECT_OUTPUT_FILES`` set to the newline-separated
list of rendered files; with explicit paths on the command line it processes
those instead.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SKIP_LINK = re.compile(
    r"\s*(?:<!--(?:(?!-->).)*?skip link(?:(?!-->).)*?-->\s*)?"
    r'(<a href="#[^"]+" class="skip-to-content">[^<]*</a>)',
    re.IGNORECASE | re.DOTALL,
)
BODY_OPEN = re.compile(r"<body\b[^>]*>", re.IGNORECASE)


def move_skip_link(html: str) -> str:
    """Return ``html`` with its single skip link moved to right after ``<body>``.

    Pages without a skip link or without a ``<body>`` tag are returned unchanged,
    as are pages where the link already follows ``<body>``. More than one skip
    link is a contract violation (the include must be the only source).
    """
    matches = list(SKIP_LINK.finditer(html))
    if not matches:
        return html
    if len(matches) > 1:
        raise ValueError(f"expected one skip link, found {len(matches)}")
    body = BODY_OPEN.search(html)
    if body is None:
        return html
    match = matches[0]
    link = match.group(1)
    if match.start() == body.end():
        return html
    without = html[: match.start()] + html[match.end() :]
    body = BODY_OPEN.search(without)
    return without[: body.end()] + "\n" + link + without[body.end() :]


def rendered_html_files(argv: list[str]) -> list[Path]:
    """Resolve the rendered HTML files to process."""
    if argv:
        names = argv
    else:
        names = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").splitlines()
    return [Path(name) for name in names if name.strip().endswith(".html")]


def main(argv: list[str] | None = None) -> int:
    """Rewrite each rendered page in place; return a process exit code."""
    for path in rendered_html_files(sys.argv[1:] if argv is None else argv):
        if not path.is_file():
            continue
        original = path.read_bytes().decode("utf-8")
        updated = move_skip_link(original)
        if updated != original:
            path.write_bytes(updated.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
