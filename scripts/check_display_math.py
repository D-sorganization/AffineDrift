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

# Both textbooks. The Geometry of Motion mirror was added once the delimiter
# handling below could see content-bearing delimiters -- until then it reported
# two false positives there, which is why the scope had stayed on one book.
# The wider `articles/` tree has not been swept for this and is not gated yet.
ROOTS = (
    Path("articles/The_Physics_of_Golf/quarto"),
    Path("articles/The_Geometry_of_Motion/quarto"),
)

# Pandoc renders a raw LaTeX maths environment in a .qmd as display maths --
# `\begin{equation} ... \end{equation}` becomes `\[ ... \]`, verified against a
# probe file. The Geometry of Motion mirror uses that form throughout, so it is
# maths, not undelimited maths, and must never be flagged.
RAW_MATH_OPEN = re.compile(
    r"^\s*\\begin\{(equation|align|gather|multline|displaymath|eqnarray)\*?\}"
)
RAW_MATH_CLOSE = re.compile(
    r"^\s*\\end\{(equation|align|gather|multline|displaymath|eqnarray)\*?\}"
)

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


def math_lines(lines: list[str]) -> tuple[int, set[int]]:
    """Count `$$` tokens outside code, and the line numbers they enclose.

    Matching on lines that are *only* `$$` misses the form where content sits
    on the delimiter line:

        $$J_c = \\begin{bmatrix}
        -\\ell_1 \\sin\\theta_1 & -\\ell_2 \\sin\\theta_2
        \\end{bmatrix},$$

    That is valid display maths, but a lone-`$$` matcher never sees the opener
    and then reports the matrix rows as undelimited. Counting the tokens
    themselves handles every form -- lone delimiters, one-line `$$ x $$`, and
    content-bearing delimiters alike.
    """
    inside: set[int] = set()
    in_fence = False
    depth = 0
    total = 0
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        occurrences = line.count("$$")
        if depth:
            inside.add(number)
        for _ in range(occurrences):
            total += 1
            depth ^= 1
            if depth:
                inside.add(number)
    return total, inside


def scan(path: Path) -> tuple[int | None, list[tuple[int, str]]]:
    """Return (odd delimiter count or None, bare maths lines)."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    delims, inside = math_lines(lines)
    if delims % 2:
        return delims, []

    in_fence = False
    in_raw_math = False
    bare: list[tuple[int, str]] = []
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or number in inside or "$$" in line:
            continue
        if RAW_MATH_OPEN.match(line):
            in_raw_math = True
            continue
        if RAW_MATH_CLOSE.match(line):
            in_raw_math = False
            continue
        if in_raw_math:
            continue
        if suspicious(line):
            bare.append((number, line.strip()))
    return None, bare


def main() -> int:
    problems = 0
    checked = 0

    for path in sorted(p for root in ROOTS for p in root.rglob("*.qmd")):
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
