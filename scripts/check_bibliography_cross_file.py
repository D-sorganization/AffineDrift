#!/usr/bin/env python3
"""Check that a citation key means the same paper in every bibliography that defines it.

The repository carries several `.bib` files, and the site renders against
most of them at once. When two files define the same key, citeproc resolves
to whichever is listed first -- so a key that means different things in
different files silently cites the wrong paper, and which paper depends on
render order rather than on anything an author wrote.

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

A second, related failure mode is the same paper carried under *different*
keys in different files (issue #4547: 183 duplicated keys and DOIs sitting
under mismatched keys such as ``Penner2001``/``penner2003`` across the seven
files this project loads together). Two entries for the same DOI describing
different work is worse than a key collision -- it means one of them has the
wrong facts attached to a real identifier. This module also checks for that,
by DOI, with the same offline title/year signature used for keys.

Several files are exempt from the duplicate-DOI check: ``golf_physics.bib``
and ``geometry_of_motion.bib`` are each also loaded by their own independent
Quarto book project (see the ``bibliography:`` lists under
``articles/*/quarto/_quarto.yml``). The rest are each the sole ``bibliography:``
of at least one page's own front matter -- a per-page bibliography *replaces*
the project-level list for that page rather than merging with it, so that page
can only ever resolve a citation against this one file, regardless of what any
other file defines: ``proximal-distal-energy.bib``
(``articles/proximal-distal-a-journey-through-the-swing.qmd``),
``affine-drift.bib`` (``drifter-manifesto.qmd`` and the Theory Part 2-5
chapters) and ``articles/tangent-hyperplane-articles/references.bib`` (its own
thesis and CRITIC pages). In every case the same reference legitimately has
its own local copy when both the exempt page/book and something else cite it.
That is not the citeproc first-wins hazard this file exists to catch; removing
any of those copies would leave a citation on the page or book that depends on
it unresolved.

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

Exits 0 when every shared key agrees and no non-exempt DOI is duplicated, 1
otherwise.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BIBS = [
    REPO / "references/affine-drift.bib",
    REPO / "references/impact-acoustics.bib",
    REPO / "references/proximal-distal-energy.bib",
    REPO / "articles/The_Physics_of_Golf/golf_physics.bib",
    REPO / "articles/The_Geometry_of_Motion/geometry_of_motion.bib",
    REPO / "articles/tangent-hyperplane-articles/references.bib",
    REPO / "articles/tangent-hyperplane-contraction/references.bib",
    REPO / "articles/proximal_distal_energy_transfer/references.bib",
]

# Loaded by their own independent Quarto book project, or as the sole
# per-page `bibliography:` of a page that therefore cannot see any other file,
# in addition to this project's root `_quarto.yml` -- see the module
# docstring. Keyed by path relative to the repo root, not by basename: three
# of the files in BIBS are all named "references.bib", so a basename would
# exempt siblings that have no standalone project or page of their own.
STANDALONE_LINKED = {
    "articles/The_Physics_of_Golf/golf_physics.bib",
    "articles/The_Geometry_of_Motion/geometry_of_motion.bib",
    "articles/tangent-hyperplane-contraction/references.bib",
    "articles/tangent-hyperplane-articles/references.bib",
    "references/proximal-distal-energy.bib",
    "references/affine-drift.bib",
}


def label(path: Path) -> str:
    """A display/exemption key unique across BIBS, unlike ``path.name``."""
    return path.relative_to(REPO).as_posix()


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
    """Return ``{key: {'title': ..., 'year': ..., 'doi': ...}}`` for one .bib file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found: dict[str, dict[str, str]] = {}
    matches = list(ENTRY.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start() : end]
        found[match.group(2)] = {
            "title": braced_field(body, "title"),
            "year": braced_field(body, "year"),
            "doi": braced_field(body, "doi").strip().lower().rstrip("."),
        }
    return found


def signature(fields: dict[str, str]) -> str:
    """Reduce an entry to what identifies the work, ignoring formatting."""
    title = re.sub(r"[^a-z0-9]", "", fields.get("title", "").lower())
    return f"{title}|{fields.get('year', '')}"


def duplicate_dois(
    doi_owners: dict[str, list[tuple[str, str, dict[str, str]]]],
) -> dict[str, list[tuple[str, str, dict[str, str]]]]:
    """Return DOI groups with an avoidable duplicate, excluding standalone copies.

    A copy in a ``STANDALONE_LINKED`` file is never avoidable: that file is
    also loaded by its own independent Quarto book project, so removing its
    copy would break that book's standalone build regardless of what any other
    file does. A group is only a violation when *more than one* of its members
    sits outside that set -- i.e. there is still a copy that nothing requires
    to exist where it is.
    """
    shared = {d: v for d, v in doi_owners.items() if len(v) > 1}
    violations = {}
    for doi, members in shared.items():
        avoidable = [m for m in members if m[0] not in STANDALONE_LINKED]
        if len(avoidable) > 1:
            violations[doi] = members
    return violations


def main() -> int:
    owners: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    doi_owners: dict[str, list[tuple[str, str, dict[str, str]]]] = defaultdict(list)
    present = 0
    for path in BIBS:
        if not path.is_file():
            continue
        present += 1
        for key, fields in entries(path).items():
            owners[key].append((path.name, fields))
            if fields.get("doi"):
                doi_owners[fields["doi"]].append((label(path), key, fields))

    shared = {k: v for k, v in owners.items() if len(v) > 1}
    disagreeing = {k: v for k, v in shared.items() if len({signature(f) for _n, f in v}) > 1}
    dup_dois = duplicate_dois(doi_owners)

    print(f"{present} bibliograph{'y' if present == 1 else 'ies'}, {len(owners)} distinct keys")
    print(f"  defined in more than one file: {len(shared)}")
    print(f"  disagreeing about the work:    {len(disagreeing)}")
    print(f"  duplicate DOIs under different keys: {len(dup_dois)}")

    if not disagreeing and not dup_dois:
        print("\nEvery shared key means the same paper, and no DOI is duplicated.")
        return 0

    if disagreeing:
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

    if dup_dois:
        print("\nA DOI below is carried by more than one key -- the same paper is a")
        print("literal duplicate bibliography entry, not just a citeproc resolution hazard:")
        for doi, defs in sorted(dup_dois.items()):
            print(f"\n  {doi}")
            for name, key, fields in defs:
                title = fields.get("title") or "<no title>"
                print(f"      [{name}] @{key}  {title[:72]}")
        print(
            "\nConsolidate to one entry under whichever key the site already cites most, "
            "merge in any field the losing entries carry that the survivor lacks, and "
            "rewrite the losing keys' citations to the survivor."
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())
