"""Fail when display maths has lost its `$$` delimiters.

Pandoc reads an undelimited equation as a paragraph: it consumes each
`\\command` as unknown inline markup and keeps the punctuation. ch08 stated the
triple-pendulum equations of motion this way, and the page shipped

    The equations of motion for a planar triple pendulum are: () + (, ) + () =

with the equation replaced by punctuation. `_book/ch08_triple_pendulum.html`
contained zero MathJax display blocks. Nothing caught it: `scan_quarto_syntax.py`
checks that `$...$` spans parse and cannot see maths that has no delimiters to
parse; an equation with no `$$` cannot carry a `{#eq-...}` label, so the
cross-reference checker sees nothing unresolved; and `quarto render` exits 0.

Two traps are worth stating, because the first scan written for this fell into
both and reported 57 sites where there were 24.

A whole equation written on one line -- `$$ x = y $$` -- opens and closes on
that line. Toggling an "inside maths" flag on every line beginning `$$` inverts
the flag from there on, so everything after it is misread. Those are skipped.

An unmatched `$$` anywhere makes the rest of the file unreadable by any such
scan, so an odd delimiter count is reported as its own finding rather than
scanned past.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Scoped to the Physics of Golf book, which is clean. The wider `articles/`
# tree has the same defect at much larger scale -- `drifter-manifesto.qmd` and
# `The_Geometry_of_Motion/quarto/` carry undelimited matrices and raw
# `\begin{equation}` blocks -- and is tracked separately. Widen this once those
# are reconciled.
ROOT = Path("articles/The_Physics_of_Golf/quarto")

FENCE = re.compile(r"^\s*(?:```+|~~~+)")
DELIM = re.compile(r"^\s*\$\$\s*(?:\{#[^}]*\})?\s*$")
ONELINE = re.compile(r"^\s*\$\$.+\$\$\s*(?:\{#[^}]*\})?\s*$")
STARTS_LATEX = re.compile(
    r"^\s*\\(?:bm|frac|begin|end|sum|int|left|text|mathcal|dot|ddot|partial)\b"
)
ALIGNED = re.compile(r"(?:&=|&\\approx|&\\quad|\S\s+&\s+\S)")
# Prose, lists, tables and code all legitimately contain '&' or a backslash.
# Numbered reference lists are the worst offenders: "10. Jouffroy, J., &
# Slotine, J. J. E. (2004)" trips an alignment heuristic every time.
PROSE = re.compile(r"^\s*(?:\||[-*+]\s|>|#|\*\*|`|\d+\.\s)")


def suspicious(line: str) -> bool:
    """A maths line, as distinct from prose that merely contains an ampersand."""
    if PROSE.match(line) or "`" in line:
        return False
    # A line carrying inline `$...$` is a sentence with maths in it, not a
    # display block that lost its fences.
    if "$" in line:
        return False
    if STARTS_LATEX.match(line):
        return True
    # An ampersand alone is not evidence; an ampersand in a line that also
    # carries a LaTeX command is.
    return bool(ALIGNED.search(line) and "\\" in line)


def scan(path: Path) -> tuple[int | None, list[tuple[int, str]]]:
    """Return (odd delimiter count or None, bare maths lines)."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    in_fence = False
    delims = 0
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or ONELINE.match(line):
            continue
        if DELIM.match(line):
            delims += 1
    if delims % 2:
        return delims, []

    in_fence = in_math = False
    bare: list[tuple[int, str]] = []
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or ONELINE.match(line):
            continue
        if DELIM.match(line):
            in_math = not in_math
            continue
        if not in_math and suspicious(line):
            bare.append((number, line.strip()))
    return None, bare


def main() -> int:
    problems = 0
    checked = 0

    for path in sorted(ROOT.rglob("*.qmd")):
        checked += 1
        odd, bare = scan(path)
        if odd is not None:
            problems += 1
            print(f"  {path.as_posix()}: {odd} '$$' delimiters -- a maths fence never closes")
            continue
        for number, text in bare:
            problems += 1
            print(
                f"  {path.as_posix()}:{number}: display maths with no '$$' -- Pandoc renders "
                f"this as a paragraph and drops the commands: {text[:60]}"
            )

    if problems:
        print(f"\n  {problems} equation(s) that will not render as maths")
        return 1

    print(f"  {checked} file(s) checked, all display maths is delimited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
