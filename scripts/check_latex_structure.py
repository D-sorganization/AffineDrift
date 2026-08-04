#!/usr/bin/env python3
"""Structural integrity checks for the LaTeX textbook sources.

Runs in seconds with no TeX distribution installed, so it can gate every pull
request while a full ``latexmk`` build runs only when LaTeX sources change.

Every rule here corresponds to a defect found in the 2026-07-31 content review,
each of which reached ``main`` and survived for months because nothing checked:

1. Stray ``\\begin{document}``/``\\end{document}`` in an included chapter. A stray
   ``\\end{document}`` in a Volume 0 chapter silently truncated that book after
   chapter 3 -- roughly 8,400 of 9,366 lines never reached the PDF.
2. Unbalanced environments. Five Physics of Golf chapters had unclosed
   environments; because one of them is included before eight others, it blocked
   those eight from compiling.
3. Files ending mid-sentence, which is what truncation looks like in a diff.
4. Missing ``\\end{document}`` in a master file.
5. Unclosed ``\\section``/``\\subsection`` braces, which arrive when Markdown is
   pasted into LaTeX.
6. Markdown code fences, same origin.
7. Unescaped ``%``. A bare percent starts a comment, so it silently deletes the
   rest of its line from the PDF.
8. Citation keys that resolve to no bibliography entry, and ``\\cite{}`` commands
   containing prose instead of a key.

Four false positives this checker deliberately avoids, each encountered while
developing it against this repository:

* ``\\begin{...}`` inside a ``%`` comment must not be counted. A comment in
  ``Volume_0/main.tex`` explaining a compatibility alias mentions
  ``\\begin{algorithmic}``, and counting it reports that file as unbalanced.
* Only a ``%`` **directly after a digit** is a forgotten percent sign. A ``%``
  elsewhere is an ordinary trailing comment (``\\usepackage{tikz} % for figures``)
  or the line-continuation idiom (``\\epigraph{%``). An earlier draft flagged any
  ``%`` with text after it, which fired on nearly every preamble line.
* A section title may wrap across source lines, so brace balance is accumulated
  forward rather than judged one line at a time.
* A citation key may contain non-ASCII letters (``Schöner2003``). Prose written
  into a ``\\cite{}`` is detected by whitespace, not by character class.

Usage::

    python3 scripts/check_latex_structure.py
    python3 scripts/check_latex_structure.py --root articles --json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Environments whose contents are verbatim: LaTeX markup inside them is literal
# text, so no rule below should fire within one.
VERBATIM_ENVIRONMENTS = frozenset(
    {"lstlisting", "verbatim", "minted", "Verbatim", "alltt", "tcblisting"}
)

# A file legitimately ends on one of these; they are layout commands, not prose.
ALLOWED_TERMINAL_COMMANDS = frozenset(
    {
        r"\cleardoublepage",
        r"\clearpage",
        r"\newpage",
        r"\endinput",
        r"\end{document}",
    }
)

# A sentence or a closed group ends with one of these.
TERMINAL_CHARACTERS = frozenset(".}]!?:;,")

BEGIN_PATTERN = re.compile(r"\\begin\{([A-Za-z*]+)\}")
END_PATTERN = re.compile(r"\\end\{([A-Za-z*]+)\}")
SECTION_PATTERN = re.compile(r"\\(?:sub){0,2}section\*?\{")
CITE_PATTERN = re.compile(r"\\([a-zA-Z]*cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")

# Macros whose name contains "cite" but which are NOT citations. `\citeneeded`
# is defined in golf_physics.sty as a deliberate, visible "[citation needed: ...]"
# marker whose argument is a description of the source still wanted. Flagging it
# would penalise the project for being honest about what it has not sourced, and
# a checker that fires on honest markers trains people to ignore it.
NON_CITATION_COMMANDS = frozenset({"citeneeded", "citationneeded", "nocite"})
BIB_ENTRY_PATTERN = re.compile(r"^@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
MARKDOWN_FENCE_PATTERN = re.compile(r"^\s*```")
# A '%' directly after a digit is a percent *sign* the author forgot to escape,
# which silently deletes the rest of the line. A '%' anywhere else is almost
# always an ordinary trailing comment ("\usepackage{tikz} % for figures") and
# must not be flagged -- that would fire on nearly every preamble line.
UNESCAPED_PERCENT_PATTERN = re.compile(r"(?<=[0-9])(?<!\\)%")
BIBLIOGRAPHY_PATTERN = re.compile(r"\\(?:bibliography|addbibresource)\{([^}]+)\}")

# A citation key is a single token. The reliable signal for prose written into a
# \cite{} is whitespace inside the key -- not character class, since real keys
# legitimately contain non-ASCII letters (e.g. 'Schoner2003' written 'Schöner2003').
PROSE_KEY_PATTERN = re.compile(r"\s")

# How many lines a section title may wrap across before we call it unbalanced.
# Titles spanning two or three source lines are ordinary LaTeX.
MAX_SECTION_CONTINUATION_LINES = 6


@dataclass(frozen=True)
class Finding:
    """A single structural defect, located precisely enough to act on."""

    path: str
    line: int
    rule: str
    message: str

    def render(self) -> str:
        location = f"{self.path}:{self.line}" if self.line else self.path
        return f"{location}: [{self.rule}] {self.message}"


@dataclass
class SourceFile:
    """A LaTeX source with comments and verbatim blocks already accounted for."""

    path: Path
    raw_lines: list[str]
    # Lines with comments stripped; verbatim content blanked. Index-aligned with
    # raw_lines so a finding can always cite a real line number.
    code_lines: list[str] = field(default_factory=list)
    verbatim_flags: list[bool] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> SourceFile:
        raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        source = cls(path=path, raw_lines=raw_lines)
        source._analyse()
        return source

    def _analyse(self) -> None:
        in_verbatim = False
        for raw in self.raw_lines:
            begins_verbatim = _names_in(BEGIN_PATTERN, raw) & VERBATIM_ENVIRONMENTS
            ends_verbatim = _names_in(END_PATTERN, raw) & VERBATIM_ENVIRONMENTS

            self.verbatim_flags.append(in_verbatim)
            if in_verbatim:
                # Inside verbatim nothing is markup, except the closing command.
                self.code_lines.append(raw if ends_verbatim else "")
            else:
                self.code_lines.append(_strip_comment(raw))

            if begins_verbatim and not ends_verbatim:
                in_verbatim = True
            elif ends_verbatim:
                in_verbatim = False

    @property
    def is_master(self) -> bool:
        """True for a document root rather than an included chapter."""
        return self.path.name == "main.tex" or r"\documentclass" in "\n".join(self.raw_lines[:40])


def _strip_comment(line: str) -> str:
    """Remove a trailing LaTeX comment, respecting ``\\%``."""
    for index, char in enumerate(line):
        if char == "%" and (index == 0 or line[index - 1] != "\\"):
            return line[:index]
    return line


def _names_in(pattern: re.Pattern[str], text: str) -> set[str]:
    return {match.group(1) for match in pattern.finditer(text)}


def check_document_environments(source: SourceFile) -> list[Finding]:
    """A chapter must never open or close the document."""
    if source.is_master:
        return []
    findings: list[Finding] = []
    for number, line in enumerate(source.code_lines, start=1):
        for match in re.finditer(r"\\(begin|end)\{document\}", line):
            findings.append(
                Finding(
                    path=str(source.path),
                    line=number,
                    rule="stray-document",
                    message=(
                        f"\\{match.group(1)}{{document}} in an included file. "
                        "LaTeX stops at the first \\end{document}, silently "
                        "dropping every chapter after this one."
                    ),
                )
            )
    return findings


def check_environment_balance(source: SourceFile) -> list[Finding]:
    """Every ``\\begin`` needs its ``\\end``, counted per environment name."""
    counts: dict[str, int] = {}
    first_seen: dict[str, int] = {}
    for number, line in enumerate(source.code_lines, start=1):
        for name in BEGIN_PATTERN.findall(line):
            counts[name] = counts.get(name, 0) + 1
            first_seen.setdefault(name, number)
        for name in END_PATTERN.findall(line):
            counts[name] = counts.get(name, 0) - 1
            first_seen.setdefault(name, number)

    findings: list[Finding] = []
    for name, net in sorted(counts.items()):
        if net == 0:
            continue
        unclosed = net > 0
        findings.append(
            Finding(
                path=str(source.path),
                line=first_seen.get(name, 0),
                rule="unbalanced-environment",
                message=(
                    f"{'unclosed' if unclosed else 'over-closed'} environment "
                    f"'{name}' (net {net:+d})"
                ),
            )
        )
    return findings


def check_truncation(source: SourceFile) -> list[Finding]:
    """A file ending mid-sentence is what truncation looks like."""
    for number in range(len(source.raw_lines), 0, -1):
        text = source.raw_lines[number - 1].strip()
        if not text:
            continue
        if text.startswith("%") or text in ALLOWED_TERMINAL_COMMANDS:
            return []
        if text[-1] in TERMINAL_CHARACTERS:
            return []
        return [
            Finding(
                path=str(source.path),
                line=number,
                rule="truncated-file",
                message=(
                    f"file ends mid-sentence: {text[:70]!r}. Expected sentence "
                    "punctuation, a closing brace, or a layout command."
                ),
            )
        ]
    return []


def check_master_has_end_document(source: SourceFile) -> list[Finding]:
    if not source.is_master:
        return []
    if any(r"\end{document}" in line for line in source.code_lines):
        return []
    return [
        Finding(
            path=str(source.path),
            line=len(source.raw_lines),
            rule="missing-end-document",
            message="master file has no \\end{document}",
        )
    ]


def check_section_braces(source: SourceFile) -> list[Finding]:
    """An unclosed section argument is how Markdown paste damage presents.

    A section title may legitimately wrap across source lines, so balance is
    accumulated forward rather than judged one line at a time.
    """
    findings: list[Finding] = []
    total = len(source.code_lines)
    for index, line in enumerate(source.code_lines):
        match = SECTION_PATTERN.search(line)
        if match is None:
            continue

        depth = 0
        resolved = False
        last_index = min(index + MAX_SECTION_CONTINUATION_LINES, total)
        for offset in range(index, last_index):
            text = source.code_lines[offset]
            start = match.end() - 1 if offset == index else 0
            for char in text[start:]:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        resolved = True
                        break
            if resolved:
                break

        if not resolved:
            findings.append(
                Finding(
                    path=str(source.path),
                    line=index + 1,
                    rule="unclosed-section-brace",
                    message=(f"section command's argument is never closed: {line.strip()[:70]!r}"),
                )
            )
    return findings


def check_markdown_fences(source: SourceFile) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(source.raw_lines, start=1):
        if source.verbatim_flags[number - 1]:
            continue
        if MARKDOWN_FENCE_PATTERN.match(line):
            findings.append(
                Finding(
                    path=str(source.path),
                    line=number,
                    rule="markdown-fence",
                    message=(
                        "Markdown code fence in LaTeX. Use lstlisting or minted; "
                        "raw code outside a verbatim environment will not typeset."
                    ),
                )
            )
    return findings


def check_unescaped_percent(source: SourceFile) -> list[Finding]:
    """A bare ``%`` deletes the rest of its line from the output."""
    findings: list[Finding] = []
    for number, raw in enumerate(source.raw_lines, start=1):
        if source.verbatim_flags[number - 1] or raw.lstrip().startswith("%"):
            continue
        match = UNESCAPED_PERCENT_PATTERN.search(raw)
        if match is None:
            continue
        findings.append(
            Finding(
                path=str(source.path),
                line=number,
                rule="unescaped-percent",
                message=(
                    "unescaped '%' with text after it silently deletes the rest "
                    f"of the line: {raw.strip()[:70]!r}. Write \\% for a percent sign."
                ),
            )
        )
    return findings


def collect_bib_keys(bib_paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in bib_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        keys.update(BIB_ENTRY_PATTERN.findall(text))
    return keys


def check_citations(source: SourceFile, known_keys: set[str]) -> list[Finding]:
    """Citation keys must resolve, and must actually be keys."""
    findings: list[Finding] = []
    for number, line in enumerate(source.code_lines, start=1):
        for match in CITE_PATTERN.finditer(line):
            if match.group(1) in NON_CITATION_COMMANDS:
                continue
            argument = match.group(2)
            for key in (part.strip() for part in argument.split(",")):
                if not key:
                    continue
                if PROSE_KEY_PATTERN.search(key):
                    findings.append(
                        Finding(
                            path=str(source.path),
                            line=number,
                            rule="prose-in-cite",
                            message=(
                                f"\\cite{{}} contains prose, not a key: {key[:70]!r}. "
                                "Source the claim, derive it, or mark it an assumption."
                            ),
                        )
                    )
                elif known_keys and key not in known_keys:
                    findings.append(
                        Finding(
                            path=str(source.path),
                            line=number,
                            rule="unresolved-citation",
                            message=f"citation key '{key}' has no bibliography entry",
                        )
                    )
    return findings


def discover_bibliographies(root: Path) -> list[Path]:
    return sorted(root.rglob("*.bib"))


def fingerprint(finding: Finding) -> str:
    """Identity of a finding that survives edits elsewhere in the same file.

    Deliberately excludes the line number: fixing an unrelated defect earlier in
    a file shifts every later line and would otherwise present every known
    finding as new.
    """
    return f"{Path(finding.path).as_posix()}|{finding.rule}|{finding.message[:80]}"


def load_baseline(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("accepted", []))


def write_baseline(path: Path, findings: list[Finding]) -> None:
    payload = {
        "_comment": (
            "Known structural defects. "
            "The check fails only on findings NOT listed here, so the corpus cannot get "
            "worse while these are worked off. Shrink this file as issues close; never "
            "grow it to silence a new defect."
        ),
        "accepted": sorted({fingerprint(item) for item in findings}),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def check_file(source: SourceFile, known_keys: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_document_environments(source))
    findings.extend(check_environment_balance(source))
    findings.extend(check_truncation(source))
    findings.extend(check_master_has_end_document(source))
    findings.extend(check_section_braces(source))
    findings.extend(check_markdown_fences(source))
    findings.extend(check_unescaped_percent(source))
    findings.extend(check_citations(source, known_keys))
    return findings


def run(root: Path, exclude: tuple[str, ...] = ()) -> list[Finding]:
    """Check every ``.tex`` file under ``root``."""
    findings: list[Finding] = []
    known_keys = collect_bib_keys(discover_bibliographies(root))
    for path in sorted(root.rglob("*.tex")):
        relative = path.as_posix()
        if any(fragment in relative for fragment in exclude):
            continue
        findings.extend(check_file(SourceFile.load(path), known_keys))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("articles"),
        help="directory to scan (default: articles)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="path fragment to skip; repeatable",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--rule",
        action="append",
        default=[],
        help="report only these rules; repeatable",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="JSON file of already-known findings; only new ones fail the run",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="record the current findings as the accepted baseline and exit 0",
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        print(f"error: {args.root} is not a directory", file=sys.stderr)
        return 2

    findings = run(args.root, tuple(args.exclude))
    if args.rule:
        findings = [item for item in findings if item.rule in set(args.rule)]

    if args.write_baseline:
        if args.baseline is None:
            print("error: --write-baseline requires --baseline", file=sys.stderr)
            return 2
        write_baseline(args.baseline, findings)
        print(f"Recorded {len(findings)} finding(s) as the baseline in {args.baseline}.")
        return 0

    accepted = load_baseline(args.baseline) if args.baseline else set()
    new_findings = [item for item in findings if fingerprint(item) not in accepted]
    resolved = len(findings) - len(new_findings)

    if args.json:
        print(json.dumps([vars(item) for item in new_findings], indent=2))
        return 1 if new_findings else 0

    for item in new_findings:
        print(item.render())

    if new_findings:
        counts: dict[str, int] = {}
        for item in new_findings:
            counts[item.rule] = counts.get(item.rule, 0) + 1
        print(f"\n{len(new_findings)} NEW structural problem(s):", file=sys.stderr)
        for rule, count in sorted(counts.items(), key=lambda pair: -pair[1]):
            print(f"  {count:5d}  {rule}", file=sys.stderr)
        return 1

    if accepted:
        print(
            f"No new structural problems. {resolved} known finding(s) still "
            f"present from the baseline; see its _comment for why each is still there."
        )
    else:
        print("No structural problems found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
