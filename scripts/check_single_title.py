"""Validate that every page renders exactly one accessible H1 title.

Quarto renders a YAML `title:` as an `<h1>`, and a body `# Heading` as another
one. A chapter carrying both ships two, numbered separately:

    <h1>3&nbsp; The Language of Motion</h1>    <- the id'd body heading
    <h1>4 The Language of Motion</h1>          <- the YAML title

Every chapter number after it is then inflated (#3700, #3705).

Conversely, pages using `page-layout: full` hide Quarto's generated
`#title-block-header` in CSS (`styles.css`), because landing and hub pages
author custom layout and hero elements (#3917). Such full-layout pages MUST
author exactly one visible `<h1>` in their template markup or markdown body.

Standalone articles that use YAML `title:` must start body sections at `## ` (H2)
so they do not emit multiple document-level `<h1>` headings.

This script enforces:
  1. No duplicate titles between YAML `title:` and body `# Heading`.
  2. No blank first lines after opening `---` in frontmatter.
  3. Every `page-layout: full` page authors exactly one visible `<h1>` (HTML or Markdown).
  4. Standalone articles with YAML `title:` do not emit multiple body `# ` H1 headings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOTS = (
    Path("articles"),
    Path("pages"),
    Path("resources"),
    Path("models"),
    Path("repositories"),
    Path("books"),
    Path("critiques"),
    Path("index.qmd"),
    Path("404.qmd"),
)
EXEMPT: set[str] = set()

INCLUDE = re.compile(r"\{\{<\s*include\s+([^\s>]+)")
FENCE = re.compile(r"^\s*(?:`{3,}|~{3,})")
H1 = re.compile(r"^#\s+\S")
HTML_H1 = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
TITLE = re.compile(r"^title:\s*(\S.*?)\s*$")
PAGE_LAYOUT_FULL = re.compile(r"^page-layout:\s*full\s*$", re.IGNORECASE)
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


def is_full_layout(lines: list[str]) -> bool:
    """Check if frontmatter specifies page-layout: full."""
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if in_frontmatter and PAGE_LAYOUT_FULL.match(line.strip()):
            return True
    return False


def same_heading(title: str, heading: str) -> bool:
    """Is the YAML title the same heading as the body H1, not a different one?"""
    return _normalise(title) == _normalise(ATTRS.sub("", heading.lstrip("# ").strip()))


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", CHAPTER_PREFIX.sub("", text).lower())


def blank_first_line(lines: list[str]) -> bool:
    """A YAML block must start on the line after the opening `---`."""
    return len(lines) > 1 and lines[0].strip() == "---" and not lines[1].strip()


def fragments(root: Path) -> set[str]:
    """Files that another file pulls in with `{{< include >}}`."""
    included: set[str] = set()
    if root.is_file() and root.suffix == ".qmd":
        text = root.read_text(encoding="utf-8", errors="replace")
        for target in INCLUDE.findall(text):
            included.add(Path(target).name)
    elif root.is_dir():
        for path in root.rglob("*.qmd"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for target in INCLUDE.findall(text):
                included.add(Path(target).name)
    return included


def body_h1_list(lines: list[str]) -> list[str]:
    """All real Markdown H1 headings outside fenced code blocks."""
    h1s: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and H1.match(line):
            h1s.append(line.strip())
    return h1s


def body_h1(lines: list[str]) -> str | None:
    """First real H1 outside fenced code, or None."""
    h1s = body_h1_list(lines)
    return h1s[0] if h1s else None


def collect_paths() -> list[Path]:
    """Collect all relevant .qmd files across declared roots."""
    paths: set[Path] = set()
    for root in ROOTS:
        if root.is_file() and root.suffix == ".qmd":
            paths.add(root)
        elif root.is_dir():
            for p in root.rglob("*.qmd"):
                if any(
                    x in p.parts
                    for x in [".quarto", "docs", "node_modules", ".git", "_freeze", ".pytest_temp"]
                ):
                    continue
                paths.add(p)
    return sorted(paths)


def main() -> int:
    problems = 0
    checked = 0

    included: set[str] = set()
    for root in ROOTS:
        included.update(fragments(root))

    for path in collect_paths():
        if path.name in EXEMPT or path.name in included:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if not lines:
            continue
        checked += 1
        h1_list = body_h1_list(lines)
        heading = h1_list[0] if h1_list else None
        html_h1s = HTML_H1.findall(text)
        full_layout = is_full_layout(lines)

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

        if full_layout:
            total_h1 = len(h1_list) + len(html_h1s)
            if total_h1 == 0:
                problems += 1
                print(
                    f"  {path.as_posix()}: page-layout: full hides Quarto's title block in CSS, "
                    f"but authors no visible <h1> heading in page markup (#3917)."
                )
            elif total_h1 > 1:
                problems += 1
                print(
                    f"  {path.as_posix()}: full-layout page authors {total_h1} <h1> headings. "
                    f"Normalize to exactly one visible <h1> title."
                )
        else:
            in_book = any(
                part.endswith(("_of_Golf", "_of_Motion", "proximal_distal_energy_transfer"))
                for part in path.parts
            )
            if not in_book and title is not None and len(h1_list) > 1:
                problems += 1
                print(
                    f"  {path.as_posix()}: standalone page with YAML title emits {len(h1_list)} body "
                    f"H1 headings. Normalize body sections to start at '## ' (H2) (#3917)."
                )

    if problems:
        print(f"\n  {problems} page(s) failed title / H1 validation")
        return 1

    print(f"  {checked} page(s) checked, each renders exactly one accessible H1 title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
