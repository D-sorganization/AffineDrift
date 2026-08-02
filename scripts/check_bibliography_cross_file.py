#!/usr/bin/env python3
"""Check that a citation key means the same paper in every bibliography that defines it.

The repository carries five `.bib` files, and the site renders against several
of them at once. When two files define the same key, citeproc resolves to
whichever is listed first -- so a key that means different things in different
files silently cites the wrong paper, and which paper depends on render order
rather than on anything an author wrote.

Four keys were in that state, all found by hand and all fixed:

* ``todorov2004optimality`` -- Todorov's 2004 review in one file, the 2002
  Todorov & Jordan paper in another. Genuinely different papers.
* ``worobets2012effects`` -- a real 2012 Sports Biomechanics paper in one file;
  in the other, a Sports Engineering paper that does not exist, with both author
  first names wrong.
* ``hogan1985impedance`` -- Part I of a three-part series in one file; in the
  other, pages 1--24, which spans all three parts as though they were one paper.
* ``Silverman2014`` -- the same chapter dated 2014 in one file and 2018 in the
  other.

Two of those were multi-part series flattened into a single entry and two were
entries for papers that do not exist as recorded, which is why "the titles
differ" is not a safe thing to reconcile by picking one. This check exists so
the state cannot return unnoticed.

What it does **not** do: judge whether an entry is correct. That needs CrossRef
and is what ``check_bibliography_metadata.py`` is for. This is the offline half
-- it only asks whether the files agree with each other, which is fast enough to
gate every push.

Comparison is on title and year, normalised to lowercase alphanumerics, so line
wrapping and punctuation do not matter. ``golf_physics.bib`` wraps titles across
three lines where ``geometry_of_motion.bib`` keeps them on one; an earlier
version of this comparison reported 16 false differences for exactly that
reason, and every one dissolved once fields were read by brace matching rather
than by a single-line regex.

Exits 0 when every shared key agrees, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BIBS = [
    REPO / "references/affine-drift.bib",
    REPO / "articles/The_Physics_of_Golf/golf_physics.bib",
    REPO / "articles/The_Geometry_of_Motion/geometry_of_motion.bib",
    REPO / "articles/tangent-hyperplane-articles/references.bib",
    REPO / "articles/tangent-hyperplane-contraction/references.bib",
]

ENTRY = re.compile(r"^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,", re.M)


def braced_field(body: str, name: str) -> str:
    """Return the value of ``name = {...}`` however many lines it spans.

    Brace counting rather than a line-anchored regex: a title wrapped across
    three lines is the same title, and reading only the first line makes it look
    like a different work.
    """
    match = re.search(rf"\b{name}\s*=\s*\{{", body, re.I)
    if not match:
        match = re.search(rf'\b{name}\s*=\s*"', body, re.I)
        if not match:
            return ""
        end = body.find('"', match.end())
        return re.sub(r"\s+", " ", body[match.end() : end]).strip() if end > 0 else ""
    depth, index = 1, match.end()
    while index < len(body) and depth:
        if body[index] == "{":
            depth += 1
        elif body[index] == "}":
            depth -= 1
        index += 1
    return re.sub(r"\s+", " ", body[match.end() : index - 1]).strip()


def entries(path: Path) -> dict[str, dict[str, str]]:
    """Return ``{key: {'title': ..., 'year': ...}}`` for one .bib file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found: dict[str, dict[str, str]] = {}
    matches = list(ENTRY.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start() : end]
        found[match.group(2)] = {
            "title": braced_field(body, "title"),
            "year": braced_field(body, "year"),
        }
    return found


def signature(fields: dict[str, str]) -> str:
    """Reduce an entry to what identifies the work, ignoring formatting."""
    title = re.sub(r"[^a-z0-9]", "", fields.get("title", "").lower())
    return f"{title}|{fields.get('year', '')}"


def main() -> int:
    owners: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    present = 0
    for path in BIBS:
        if not path.is_file():
            continue
        present += 1
        for key, fields in entries(path).items():
            owners[key].append((path.name, fields))

    shared = {k: v for k, v in owners.items() if len(v) > 1}
    disagreeing = {k: v for k, v in shared.items() if len({signature(f) for _n, f in v}) > 1}

    print(f"{present} bibliograph{'y' if present == 1 else 'ies'}, {len(owners)} distinct keys")
    print(f"  defined in more than one file: {len(shared)}")
    print(f"  disagreeing about the work:    {len(disagreeing)}")

    if not disagreeing:
        print("\nEvery shared key means the same paper in every file that defines it.")
        return 0

    print("\nA key below resolves to whichever file the render lists first:")
    for key, defs in sorted(disagreeing.items()):
        print(f"\n  @{key}")
        for name, fields in defs:
            title = fields.get("title") or "<no title>"
            print(f"      [{name}] {fields.get('year', '????')}  {title[:72]}")
    print(
        "\nReconcile the entries so every file describes the same work, or give the "
        "different works different keys. Do not simply copy one over the other: two of "
        "the four historical cases were multi-part series flattened into one entry."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
