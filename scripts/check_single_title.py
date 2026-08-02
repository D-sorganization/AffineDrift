"""Fail when a page would render its title twice.

Quarto renders a YAML `title:` as an `<h1>`, and a body `# Heading` as another
one. A chapter carrying both ships two, numbered separately:

    <h1>3&nbsp; The Language of Motion</h1>    <- the id'd body heading
    <h1>4 The Language of Motion</h1>          <- the YAML title

Every chapter number after it is then inflated.

This has regressed twice -- #3700 introduced it, #3705 reintroduced it by
restoring the frontmatter fields #3702 had removed -- because every other gate
passes on the broken state: the frontmatter validator sees a title, the
cross-reference checker sees its anchors, the maths scanner sees valid maths,
and `quarto render` exits 0 without a warning.

The titles cannot simply stay in the frontmatter. A `{#sec-...}` anchor attaches
to a heading and never to a YAML key, and 132 cross-references in the book
resolve to those anchors. So a chapter that is referenced has to carry its title
in the body -- which means it must not also carry one above.

`index.qmd` is exempt: its `title:` is the book title and its H1 is "Preface",
which are two different headings rather than one heading twice.

Scope is the Physics of Golf book. 29 standalone pages elsewhere in `articles/`
have the same duplication, but they predate this and are not part of a numbered
book, so removing their frontmatter titles risks changing how they are listed
elsewhere on the site. They are tracked separately; widen `ROOT` once they are
reconciled, rather than adding a baseline that would grant the book standing
permission to regress a third time.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOTS = (
    Path("articles/The_Physics_of_Golf/quarto"),
    Path("articles/The_Geometry_of_Motion/quarto"),
)
EXEMPT = {"index.qmd"}

INCLUDE = re.compile(r"\{\{<\s*include\s+([^\s>]+)")

FENCE = re.compile(r"^\s*(?:```+|~~~+)")
H1 = re.compile(r"^#\s+\S")
TITLE = re.compile(r"^title:\s*\S")


def frontmatter_title(lines: list[str]) -> bool:
    if not lines or lines[0].strip() != "---":
        return False
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return False
        if TITLE.match(lines[index]):
            return True
    return False


def blank_first_line(lines: list[str]) -> bool:
    """A YAML block must start on the line after the opening `---`.

    With a blank line there, Pandoc does not recognise the block at all: the
    `---` becomes a horizontal rule and the metadata keys render as page
    content. ch01 shipped its `description:` line as a chapter heading that way
    (#3705), which is a worse failure than the duplicate title and looks
    identical in the source unless the blank line is noticed.
    """
    return len(lines) > 1 and lines[0].strip() == "---" and not lines[1].strip()


def fragments(root: Path) -> set[str]:
    """Files that another file pulls in with `{{< include >}}`.

    Quarto discards the frontmatter of an included file, so a `title:` there is
    dead metadata and the page-level rule below does not apply. 23 of the 27
    files in the Geometry of Motion mirror are fragments; checking them as pages
    reports a dozen duplicate titles that do not exist, and an earlier pass
    "fixed" all twelve before the `<title>` tag gave it away.
    """
    included: set[str] = set()
    for path in root.rglob("*.qmd"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in INCLUDE.findall(text):
            included.add(Path(target).name)
    return included


def body_h1(lines: list[str]) -> str | None:
    """First real H1 outside fenced code, or None."""
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and H1.match(line):
            return line.strip()
    return None


def main() -> int:
    problems = 0
    checked = 0

    included = {name for root in ROOTS for name in fragments(root)}

    for path in sorted(p for root in ROOTS for p in root.rglob("*.qmd")):
        if path.name in EXEMPT or path.name in included:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines:
            continue
        checked += 1
        heading = body_h1(lines)

        if blank_first_line(lines):
            problems += 1
            print(
                f"  {path.as_posix()}: a blank line follows the opening '---', so the "
                f"frontmatter is not parsed at all and its keys render as page content"
            )
            continue

        if frontmatter_title(lines) and heading is not None:
            problems += 1
            print(
                f"  {path.as_posix()}: has a YAML 'title:' and the body heading "
                f"'{heading[:56]}' -- Quarto renders both as separate, separately "
                f"numbered <h1>. Drop the YAML title; the heading carries the anchor."
            )

    if problems:
        print(f"\n  {problems} page(s) would render their title twice")
        return 1

    print(f"  {checked} page(s) checked, each renders a single title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
