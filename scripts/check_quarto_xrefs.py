"""Fail when a Quarto cross-reference points at something that does not exist.

An unresolved `@sec-foo` does not fail the render. Quarto emits exit 0 and the
page ships with the raw key printed where the link should be:

    In the worked example (?sec-ch11:worked), suppose the hand acceleration...

The book carried 132 of these. Reading the source never finds them, because the
source looks exactly like a working reference -- the defect only exists in the
output. This check reads the source anyway, by collecting what is defined and
what is referenced and comparing the two.

One subtlety is worth stating, because it cost a wrong fix. A callout is a div:

    ## The Mass Matrix: Understanding Coupling

    ::: {.callout-note}
    ## The $3 \\times 3$ Mass Matrix for a Triple Pendulum {#sec-mass_matrix}

The second `##` is the callout's *title*, not a section. Quarto ignores an id
placed there, so the reference stays dead while the source looks correct. An id
on a heading inside a callout is therefore reported as a broken definition, not
counted as one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# One Quarto project: references resolve across the files inside it.
BOOKS = (
    Path("articles/The_Physics_of_Golf/quarto"),
    Path("articles/The_Geometry_of_Motion/quarto"),
)

PREFIXES = ("sec", "eq", "fig", "tbl", "thm", "lst")
_ALT = "|".join(PREFIXES)

DEFINITION = re.compile(r"\{#((?:" + _ALT + r")-[A-Za-z0-9_:.-]+)\}")
REFERENCE = re.compile(r"(?<![\w`])@((?:" + _ALT + r")-[A-Za-z0-9_:.-]+)")
HEADING = re.compile(r"^\s*#{1,6}\s")
FENCE = re.compile(r"^\s*(```+|~~~+)")
DIV_OPEN = re.compile(r"^:::+\s*\{")
DIV_CLOSE = re.compile(r"^:::+\s*$")
CALLOUT = re.compile(r"\.callout-")
INLINE_CODE = re.compile(r"`[^`]*`")


def trim(key: str) -> str:
    """Drop sentence punctuation that the greedy key pattern swallowed."""
    return key.rstrip(".,;:-")


def scan(
    path: Path,
) -> tuple[dict[str, tuple[Path, int]], list[tuple[str, int]], list[tuple[str, int]]]:
    """Return (definitions, references, ids stranded inside callouts)."""
    defined: dict[str, tuple[Path, int]] = {}
    referenced: list[tuple[str, int]] = []
    stranded: list[tuple[str, int]] = []

    in_fence = False
    callout_depth = 0
    depth = 0

    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if DIV_OPEN.match(line):
            depth += 1
            if CALLOUT.search(line):
                callout_depth = depth
        elif DIV_CLOSE.match(line):
            if callout_depth == depth:
                callout_depth = 0
            depth = max(0, depth - 1)

        bare = INLINE_CODE.sub("", line)

        for match in DEFINITION.finditer(bare):
            key = match.group(1)
            if HEADING.match(bare) and callout_depth:
                stranded.append((key, number))
            else:
                defined.setdefault(key, (path, number))

        for match in REFERENCE.finditer(bare):
            referenced.append((trim(match.group(1)), number))

    return defined, referenced, stranded


def main() -> int:
    books = [book for book in BOOKS if book.is_dir()]
    if not books:
        print("  no book directory found; nothing to check")
        return 0

    files: list[Path] = []
    total_defined = 0
    total_references = 0
    unresolved: list[tuple[Path, str, int]] = []
    stranded: list[tuple[Path, str, int]] = []

    # Each book is its own Quarto project, so a reference resolves against the
    # book that contains it. Pooling the two would let a missing target in one
    # be masked by a same-named target in the other.
    for book in books:
        book_files = sorted(book.glob("*.qmd"))
        files.extend(book_files)
        defined: dict[str, tuple[Path, int]] = {}
        references: list[tuple[Path, str, int]] = []
        for path in book_files:
            found, used, orphaned = scan(path)
            for key, where in found.items():
                defined.setdefault(key, where)
            references.extend((path, key, number) for key, number in used)
            stranded.extend((path, key, number) for key, number in orphaned)
        total_defined += len(defined)
        total_references += len(references)
        unresolved.extend(
            (path, key, number) for path, key, number in references if key not in defined
        )

    problems = 0

    for path, key, number in stranded:
        problems += 1
        print(
            f"  {path.name}:{number}: id '{key}' sits on a callout title, "
            f"where Quarto ignores it -- move it to the section heading"
        )

    seen: set[tuple[str, str]] = set()
    for path, key, number in unresolved:
        if (path.name, key) in seen:
            continue
        seen.add((path.name, key))
        problems += 1
        print(f"  {path.name}:{number}: reference '@{key}' has no definition anywhere in the book")

    if problems:
        print(
            f"\n  {problems} broken cross-reference(s); each renders as a literal '?key' on the site"
        )
        return 1

    print(
        f"  {total_defined} cross-reference target(s), {total_references} reference(s), "
        f"all resolved across {len(books)} book(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
