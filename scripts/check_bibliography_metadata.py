#!/usr/bin/env python3
"""Check cited bibliography entries against the CrossRef record.

Key resolution is already gated: `compile-textbooks.yml` fails the build on
"I didn't find a database entry". Nothing checks whether a resolved entry is
*correct*, and three wrong ones have been found by hand so far:

* ``Kawato1987`` carried a title, volume and page range describing a paper that
  does not exist. Only the authors and year were right.
* ``Georgopoulos1986`` spliced two papers together -- the 1982 paper's title,
  the 1986 paper's authors, a year and volume matching neither.
* A third was removed under #3611 as outright fabricated.

None of those failed a resolution check. A citation that resolves to a
nonexistent paper is worse than one that visibly fails: the broken one
announces itself, while this kind survives review and a reader who chases it
concludes the author never read what they cited.

This is a manual audit tool, not a CI gate -- it needs network access and
CrossRef coverage is uneven. Findings are advisory and every flag needs a human
look before it is called an error.

    python3 scripts/check_bibliography_metadata.py report.txt

Two false-positive modes are deliberately designed out, both learned from
running earlier versions against this repository:

1. **Absence from CrossRef is not evidence.** An 1840 French memoir, a 1961
   Soviet paper, arXiv-only preprints and Zajac's 1989 CRC Critical Reviews
   article are all real and all unindexed. An earlier version flagged 64 of 187
   entries and was mostly this. Unmatched entries are counted, never reported.
2. **A title can appear in CrossRef several times over** -- the conference
   version and the journal version, the original and a reprint, the paper and
   its erratum. Comparing against whichever record ranks first flagged
   ``Stewart1965``, ``hogan1985impedance``, ``schultz1997dopamine`` and
   ``Kepple1997`` while all four were correct. Every candidate above the title
   floor is gathered, and a problem is reported only when none of them fits.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

UA = "AffineDrift-bib-audit/2.0 (mailto:dieterolson@gmail.com)"
TITLE_FLOOR = 0.93
REPO = Path(__file__).resolve().parent.parent
BIBS = {
    "GoM": (
        REPO / "articles/The_Geometry_of_Motion/geometry_of_motion.bib",
        REPO / "articles/The_Geometry_of_Motion",
    ),
    "PoG": (
        REPO / "articles/The_Physics_of_Golf/golf_physics.bib",
        REPO / "articles/The_Physics_of_Golf",
    ),
}
ENTRY = re.compile(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", re.M)
NON_CITE = {"citeneeded", "citationneeded", "nocite"}
WANTED = {"article", "inproceedings", "incollection", "conference"}


def field(body: str, name: str) -> str:
    """Read one BibTeX field, respecting nested braces in the value."""
    m = re.search(name + r"\s*=\s*", body, re.I)
    if not m:
        return ""
    i = m.end()
    while i < len(body) and body[i] in " \t":
        i += 1
    if i >= len(body):
        return ""
    if body[i] in '{"':
        close = "}" if body[i] == "{" else '"'
        depth, j = 0, i
        while j < len(body):
            if body[j] == body[i]:
                depth += 1
            elif body[j] == close:
                depth -= 1
                if depth == 0:
                    return re.sub(r"\s+", " ", body[i + 1 : j]).strip()
            j += 1
        return ""
    tail = re.match(r"([^,\n}]*)", body[i:])
    return tail.group(1).strip() if tail else ""


def norm(s: str) -> str:
    s = re.sub(r"[{}\\]", "", s.lower())
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def first_page(value: str) -> str:
    """Leading page number, tolerating en-dashes and '187--230' style ranges."""
    parts = re.split(r"[-\u2010-\u2015]", value.replace("--", "-"), maxsplit=1)
    return re.sub(r"\D", "", parts[0]) if parts else ""


def entries(text: str):
    marks = [(m.group(2), m.group(1).lower(), m.start()) for m in ENTRY.finditer(text)]
    for i, (key, kind, start) in enumerate(marks):
        end = marks[i + 1][2] if i + 1 < len(marks) else len(text)
        yield key, kind, text[start:end]


def cited_keys(root: Path) -> set[str]:
    keys: set[str] = set()
    for path in root.rglob("*.tex"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\\([a-zA-Z]*cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}", text):
            if m.group(1) in NON_CITE:
                continue
            for k in m.group(2).split(","):
                if k.strip():
                    keys.add(k.strip())
    return keys


def crossref(title: str, author: str) -> list[dict]:
    query = {
        "query.bibliographic": title,
        "rows": "10",
        "select": "title,container-title,volume,issue,page,issued,DOI",
    }
    if author:
        query["query.author"] = author
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["message"]["items"]


def differences(entry: dict, record: dict) -> list[str]:
    year = str((record.get("issued", {}).get("date-parts") or [[""]])[0][0] or "")
    volume = str(record.get("volume") or "")
    pages = str(record.get("page") or "")
    container = (record.get("container-title") or [""])[0]

    found = []
    if entry["year"] and year and entry["year"] != year:
        found.append(f"year {entry['year']} vs {year}")
    if entry["volume"] and volume and entry["volume"] != volume:
        found.append(f"volume {entry['volume']} vs {volume}")
    if entry["pages"] and pages:
        a, b = first_page(entry["pages"]), first_page(pages)
        if a and b and a != b:
            found.append(f"first page {a} vs {b}")
    if entry["journal"] and container:
        if SequenceMatcher(None, norm(entry["journal"]), norm(container)).ratio() < 0.55:
            found.append(f"journal '{entry['journal'][:40]}' vs '{container[:40]}'")
    return found


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "bibliography-audit.txt"
    checked = confident = flagged = unmatched = failed = 0

    with out.open("w", encoding="utf-8") as fh:
        for name, (bib, root) in BIBS.items():
            text = bib.read_text(encoding="utf-8")
            used = cited_keys(root)
            for key, kind, body in entries(text):
                if kind not in WANTED or key not in used:
                    continue
                title = field(body, "title")
                if not title:
                    continue
                entry = {
                    "year": field(body, "year"),
                    "volume": field(body, "volume"),
                    "pages": field(body, "pages"),
                    "journal": field(body, "journal") or field(body, "booktitle"),
                }
                author = field(body, "author").split(" and ")[0].split(",")[0].strip()

                checked += 1
                try:
                    items = crossref(title, author)
                except Exception as exc:
                    failed += 1
                    fh.write(f"LOOKUP-FAILED {name} {key}: {exc}\n")
                    fh.flush()
                    time.sleep(1.5)
                    continue
                time.sleep(0.7)

                candidates, best_score = [], 0.0
                for item in items:
                    other = (item.get("title") or [""])[0]
                    score = SequenceMatcher(None, norm(title), norm(other)).ratio()
                    best_score = max(best_score, score)
                    if score >= TITLE_FLOOR:
                        candidates.append(item)

                if not candidates:
                    unmatched += 1
                    fh.write(f"unmatched {name} {key} (best {best_score:.2f})\n")
                    fh.flush()
                    continue

                confident += 1
                scored = sorted(
                    ((differences(entry, c), c) for c in candidates), key=lambda p: len(p[0])
                )
                diffs, record = scored[0]
                if not diffs:
                    continue

                flagged += 1
                if len(candidates) > 1:
                    diffs = [*diffs, f"({len(candidates)} same-title records; best fit shown)"]
                fh.write(
                    f"FLAG {name} {key}\n"
                    f"     {title[:96]}\n"
                    f"     {'; '.join(diffs)}\n"
                    f"     doi {record.get('DOI', '-')}\n"
                )
                fh.flush()

        summary = (
            f"\nSUMMARY: {checked} cited article/proceedings entries checked\n"
            f"  confident title match (>= {TITLE_FLOOR}): {confident}\n"
            f"  no confident match (not a finding, see module docstring): {unmatched}\n"
            f"  lookup failures: {failed}\n"
            f"  metadata mismatches to review by hand: {flagged}\n"
        )
        fh.write(summary)

    print(summary)
    print(f"full report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
