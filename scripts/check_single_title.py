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

ROOTS = (Path("articles"),)
EXEMPT: set[str] = set()

INCLUDE = re.compile(r"\{\{<\s*include\s+([^\s>]+)")

FENCE = re.compile(r"^\s*(?:```+|~~~+)")
H1 = re.compile(r"^#\s+\S")
TITLE = re.compile(r"^title:\s*(\S.*?)\s*$")
ATTRS = re.compile(r"\s*\{[^}]*\}\s*$")
CHAPTER_PREFIX = re.compile(r"^Chapter\s+\d+[:.]?\s*", re.IGNORECASE)


def frontmatter_title(lines: list[str]) -> str | None:
    """The YAML `title:` value, or None."""
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return None
        match = TITLE.match(lines[index])
        if match:
            return match.group(1).strip().strip("\"'")
    return None


def same_heading(title: str, heading: str) -> bool:
    """Is the YAML title the same heading as the body H1, not a different one?

    The defect is one heading rendered twice. A document whose `title:` names
    the document and whose first H1 is a section -- "Abstract", "Introduction",
    "Preface", "Part 1: ..." -- has two different headings and is correct. That
    is the shape of every standalone article on this site, and comparing only
    "does a title exist" flags all eleven of them.

    A "Chapter N:" prefix is ignored, because Quarto numbers chapters itself and
    #3705's restored titles carried it.
    """
    return _normalise(title) == _normalise(ATTRS.sub("", heading.lstrip("# ").strip()))


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", CHAPTER_PREFIX.sub("", text).lower())


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

        title = frontmatter_title(lines)
        if title is not None and heading is not None and same_heading(title, heading):
            problems += 1
            in_book = any(part.endswith(("_of_Golf", "_of_Motion")) for part in path.parts)
            remedy = (
                "Drop the YAML title -- in a book the heading carries the "
                "'{#sec-...}' anchor that cross-references resolve to."
                if in_book
                else "Drop the duplicate body heading -- on a standalone page the "
                "YAML title is what produces the <title> tag, and removing it "
                "leaves the page titled after its filename."
            )
            print(
                f"  {path.as_posix()}: the YAML 'title:' and the body heading "
                f"'{heading[:48]}' are the same heading, so Quarto renders it twice. {remedy}"
            )

    if problems:
        print(f"\n  {problems} page(s) would render their title twice")
        return 1

    print(f"  {checked} page(s) checked, each renders a single title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
