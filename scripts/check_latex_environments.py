"""Fail when a `.qmd` contains a LaTeX environment Pandoc will not render.

Pandoc renders maths environments in a `.qmd` and drops everything else --
silently, exit 0 -- so the content inside simply never reaches the page. This
review found it twice, and both times it was real content rather than markup:

  * 79 boxes in the Geometry of Motion mirror (#3720), including the book's
    axioms, its scope warnings, and its plain-language explanations;
  * 24 tables (#3722), including the numerical residual-scaling data that backs
    a chapter's convergence claim.

The rule was established by probing, not assumed: a page was rendered per
environment type with a unique sentinel inside it, and every non-maths
environment tested -- `table`, `tabular`, `figure`, `center`, `itemize`,
`enumerate`, `description`, `algorithm`, `quote`, `verbatim` and the custom
boxes -- lost its content. Only maths survived.

That history is why the allow-list here is maths-only rather than "things that
look standard". An earlier probe assumed `table` and `itemize` were safe
because they are ordinary LaTeX, and 24 tables stayed missing as a result.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("articles")

# Verified to render. Everything else is dropped.
MATHS = {
    "align",
    "aligned",
    "array",
    "bmatrix",
    "cases",
    "displaymath",
    "eqnarray",
    "equation",
    "gather",
    "gathered",
    "matrix",
    "multline",
    "pmatrix",
    "smallmatrix",
    "split",
    "subarray",
    "vmatrix",
    "Bmatrix",
    "Vmatrix",
}

BEGIN = re.compile(r"\\begin\{([a-zA-Z]+)\*?\}")
FENCE = re.compile(r"^\s*(?:```+|~~~+)")


def find(text: str) -> list[tuple[int, str]]:
    """(line number, environment) for each unrenderable environment."""
    found: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for name in BEGIN.findall(line):
            if name not in MATHS:
                found.append((number, name))
    return found


def main() -> int:
    problems = 0
    checked = 0
    for path in sorted(ROOT.rglob("*.qmd")):
        checked += 1
        for number, name in find(path.read_text(encoding="utf-8", errors="replace")):
            problems += 1
            print(
                f"  {path.as_posix()}:{number}: \\begin{{{name}}} is not a maths "
                f"environment, so Pandoc drops it and its content never reaches the page"
            )

    if problems:
        print(f"\n  {problems} environment(s) whose content will not render")
        return 1

    print(f"  {checked} file(s) checked, no unrenderable LaTeX environments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
