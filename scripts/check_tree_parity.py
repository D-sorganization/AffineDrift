#!/usr/bin/env python3
"""Cross-tree parity between the LaTeX textbooks and their Quarto mirrors.

Both textbooks exist twice. The LaTeX tree under ``articles/*/chapters/`` and
``articles/*/Volume_*/chapters/`` produces the PDFs; the Quarto tree under
``articles/*/quarto/`` produces the website. They are maintained by hand, and
nothing has been checking that they agree.

They have already diverged, in both directions. Issue #3321 ("canonical impact
numbers wrong/inconsistent") was closed COMPLETED on 2026-06-12, but its body
scopes itself to ``articles/The_Physics_of_Golf/quarto/`` -- so the fix reached
the website and never the book. The LaTeX text still said a golf ball weighs
150 grams while the ``.qmd`` mirror correctly said 45.93 g. The reverse also
happens: the book carried a corrected smash factor that the website did not.

This checker reports two classes of divergence:

**Coverage** -- a chapter present in one tree and absent from the other. A
reader of the website and a reader of the PDF are then reading different books.

**Canonical quantities** -- a curated set of physical values that must agree
everywhere. Comparing *every* number across a chapter pair produces far too much
noise to act on (equation numbers, section references, array indices), so this
deliberately checks only quantities that are load-bearing and have a single
correct value.

Usage::

    python3 scripts/check_tree_parity.py
    python3 scripts/check_tree_parity.py --json
    python3 scripts/check_tree_parity.py --baseline config/tree-parity-baseline.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Chapter pairs are discovered by mapping a LaTeX chapter directory to the
# Quarto directory that mirrors it, with an optional filename prefix where the
# mirror renames files.
TREE_PAIRS = [
    ("articles/The_Physics_of_Golf/chapters", "articles/The_Physics_of_Golf/quarto", ""),
    (
        "articles/The_Geometry_of_Motion/Volume_0/chapters",
        "articles/The_Geometry_of_Motion/quarto",
        "vol0_",
    ),
    (
        "articles/The_Geometry_of_Motion/Volume_I/chapters",
        "articles/The_Geometry_of_Motion/quarto",
        "",
    ),
]

# Files that are structural rather than chapters, and have no mirror by design:
# document roots, front/back matter, and the Quarto landing pages.
NON_CHAPTER_STEMS = frozenset(
    {
        "main",
        "nomenclature",
        "further_reading",
        "index",
        "volume0",
        "volume1",
        "volume2",
        "volume2_content",
        "textbook-main",
    }
)


@dataclass(frozen=True)
class SupersededValue:
    """A value the review established as wrong, which must not reappear.

    Checking for *known-wrong* values rather than extracting and diffing every
    number is a deliberate choice. General numeric extraction is unusable here:
    a pattern loose enough to catch "45.93 g" also catches "18 g" of centripetal
    acceleration, and the corpus is full of numbers that legitimately differ
    between a chapter and its mirror (equation numbers, indices, section refs).
    Encoding the specific regressions keeps every hit actionable.
    """

    name: str
    pattern: str
    correct: str
    note: str


SUPERSEDED_VALUES = [
    SupersededValue(
        name="150 g golf ball",
        pattern=r"150[- ]?(?:g\b|gram)[^.\n]{0,40}ball|ball[^.\n]{0,40}150[- ]?(?:g\b|gram)",
        correct="45.93 g",
        note="regulation maximum is 45.93 g (R&A/USGA). Fixed in .qmd by #3321, missed in .tex",
    ),
    SupersededValue(
        name="15--25 Hz shaft mode",
        pattern=r"15\s*(?:--|-|–)\s*25\s*Hz",
        correct="3--5 Hz",
        note="a driver shaft's first cantilever bending mode is ~3-5 Hz",
    ),
    SupersededValue(
        name="50--200 Hz shaft mode",
        pattern=r"50\s*(?:--|-|–)\s*200\s*Hz",
        correct="3--5 Hz",
        note="10-50x too high; correcting it reverses ch24's bandwidth argument (#3546)",
    ),
    SupersededValue(
        name="COR as an energy ratio",
        pattern=r"(?:8[0-9])\s*\\?%[^.\n]{0,60}(?:impact\s+)?kinetic\s+energy",
        correct="COR is a speed ratio",
        note="COR relates speeds, not energies; ch28's own calculation gives ~50% energy transfer",
    ),
]


@dataclass(frozen=True)
class Finding:
    kind: str
    detail: str
    tex: str = ""
    qmd: str = ""

    def render(self) -> str:
        return f"[{self.kind}] {self.detail}"


def strip_latex_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        for index, char in enumerate(line):
            if char == "%" and (index == 0 or line[index - 1] != "\\"):
                line = line[:index]
                break
        out.append(line)
    return "\n".join(out)


def chapter_stems(directory: Path, suffix: str, prefix: str = "") -> dict[str, Path]:
    """Map a normalised chapter stem to its file."""
    found: dict[str, Path] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob(f"*{suffix}")):
        stem = path.stem
        if stem in NON_CHAPTER_STEMS:
            continue
        if prefix:
            if not stem.startswith(prefix):
                continue
            stem = stem[len(prefix) :]
        found[stem] = path
    return found


def check_coverage(root: Path) -> list[Finding]:
    """Report chapters present in one tree only.

    Several LaTeX volumes share one Quarto directory, so a `.qmd` is only
    "orphaned" if *no* pair claims it. Judging that per-pair would report every
    Volume 0 mirror as missing from Volume I.
    """
    findings: list[Finding] = []
    claimed_qmd: dict[str, set[Path]] = {}

    for tex_dir, qmd_dir, prefix in TREE_PAIRS:
        tex_map = chapter_stems(root / tex_dir, ".tex")
        qmd_map = chapter_stems(root / qmd_dir, ".qmd", prefix)
        if not tex_map:
            continue

        for stem in sorted(set(tex_map) - set(qmd_map)):
            findings.append(
                Finding(
                    kind="latex-only",
                    detail=(
                        f"'{stem}' exists in {tex_dir} but has no Quarto mirror in "
                        f"{qmd_dir} -- website readers cannot reach this chapter"
                    ),
                    tex=str(tex_map[stem]),
                )
            )
        for stem in set(tex_map) & set(qmd_map):
            claimed_qmd.setdefault(qmd_dir, set()).add(qmd_map[stem])

    # Now, per shared Quarto directory, anything no pair matched is orphaned.
    for qmd_dir in {pair[1] for pair in TREE_PAIRS}:
        directory = root / qmd_dir
        if not directory.is_dir():
            continue
        claimed = claimed_qmd.get(qmd_dir, set())
        for path in sorted(directory.glob("*.qmd")):
            if path.stem in NON_CHAPTER_STEMS or path in claimed:
                continue
            findings.append(
                Finding(
                    kind="quarto-only",
                    detail=(
                        f"'{path.stem}' exists in {qmd_dir} but no LaTeX chapter maps to "
                        "it -- it will not appear in any PDF"
                    ),
                    qmd=str(path),
                )
            )
    return findings


def check_superseded_values(root: Path) -> list[Finding]:
    """Report a known-wrong value surviving anywhere in either tree.

    Scans both trees independently rather than only paired chapters, because a
    superseded value is wrong wherever it appears -- including in a chapter that
    has no mirror.
    """
    findings: list[Finding] = []
    scanned: set[Path] = set()

    for tex_dir, qmd_dir, _prefix in TREE_PAIRS:
        for directory, suffix in ((root / tex_dir, ".tex"), (root / qmd_dir, ".qmd")):
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob(f"*{suffix}")):
                if path in scanned:
                    continue
                scanned.add(path)
                text = path.read_text(encoding="utf-8", errors="replace")
                if suffix == ".tex":
                    text = strip_latex_comments(text)
                for value in SUPERSEDED_VALUES:
                    if re.search(value.pattern, text, re.IGNORECASE):
                        tree = "LaTeX" if suffix == ".tex" else "Quarto"
                        findings.append(
                            Finding(
                                kind="superseded-value",
                                detail=(
                                    f"{path.name} ({tree} tree) still contains "
                                    f"{value.name} -- should be {value.correct}. {value.note}"
                                ),
                                tex=str(path) if suffix == ".tex" else "",
                                qmd=str(path) if suffix == ".qmd" else "",
                            )
                        )
    return findings


def run(root: Path) -> list[Finding]:
    return check_coverage(root) + check_superseded_values(root)


def fingerprint(finding: Finding) -> str:
    return f"{finding.kind}|{finding.detail}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    findings = run(args.root)

    if args.write_baseline:
        if args.baseline is None:
            print("error: --write-baseline requires --baseline", file=sys.stderr)
            return 2
        args.baseline.write_text(
            json.dumps(
                {
                    "_comment": (
                        "Known LaTeX/Quarto divergences, tracked under #3499. The check "
                        "fails only on divergences NOT listed here. Shrink this file as "
                        "the trees are reconciled; never grow it to silence a new one."
                    ),
                    "accepted": sorted({fingerprint(item) for item in findings}),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Recorded {len(findings)} divergence(s) as the baseline in {args.baseline}.")
        return 0

    accepted: set[str] = set()
    if args.baseline and args.baseline.is_file():
        accepted = set(json.loads(args.baseline.read_text(encoding="utf-8")).get("accepted", []))

    new = [item for item in findings if fingerprint(item) not in accepted]

    if args.json:
        print(json.dumps([vars(item) for item in new], indent=2))
        return 1 if new else 0

    for item in new:
        print(item.render())

    if new:
        print(f"\n{len(new)} NEW cross-tree divergence(s).", file=sys.stderr)
        print(
            "A content fix must be applied to BOTH trees, or the website and the "
            "PDF drift apart. See content-development/RIGOR_GUIDE.md rule 9.",
            file=sys.stderr,
        )
        return 1

    if accepted:
        print(f"No new divergences. {len(findings)} known, tracked under #3499.")
    else:
        print("LaTeX and Quarto trees are in parity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
