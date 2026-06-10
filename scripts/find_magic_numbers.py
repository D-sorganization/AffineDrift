"""Scan article sources for uncited quantitative/empirical claims.

Pure helpers (``line_is_skippable``, ``line_has_uncited_claim``, ``scan_lines``)
are extracted so the detection logic is unit-testable without filesystem walks
(issue #3230). The ``main`` entry point preserves the original behavior: walk the
article directories and write ``magic_numbers_report.txt``.
"""

from __future__ import annotations

import os
import re

directories = [
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf",
    r"C:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion",
]

patterns = [
    r"\b\d+(?:\.\d+)?\s*(?:N|Nm|N·m|kg|m/s|mph|degrees|rad/s|ms|%)\b",  # physical units
    r"\b(?:a study|studies|researchers|experiments|measurements|data shows)\b",
]
cite_pattern = r"\\cite(?:p|t)?\{[^}]+\}|@\w+"  # \cite{...} or @Smith2020


def line_is_skippable(line: str) -> bool:
    """Return True for comment/math lines that should not be scanned."""
    clean_line = line.strip()
    if clean_line.startswith("%") or clean_line.startswith("<!-"):
        return True
    return clean_line.startswith("\\") or clean_line.startswith("$$")


def line_has_uncited_claim(line: str) -> bool:
    """Return True if *line* matches a claim pattern but carries no citation."""
    if line_is_skippable(line):
        return False
    if not any(re.search(p, line, re.IGNORECASE) for p in patterns):
        return False
    return not re.search(cite_pattern, line)


def scan_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Return ``(line_number, text)`` tuples for each uncited claim line.

    Line numbers are 1-based to match editor conventions.
    """
    findings: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if line_has_uncited_claim(line):
            findings.append((i + 1, line.strip()))
    return findings


def main() -> None:
    """Walk the article directories and write the magic-numbers report."""
    findings: dict[str, list[tuple[int, str]]] = {}
    for d in directories:
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith((".tex", ".qmd")):
                    path = os.path.join(root, f)
                    try:
                        with open(path, encoding="utf-8") as file_obj:
                            lines = file_obj.readlines()
                    except UnicodeDecodeError:
                        continue
                    matches = scan_lines(lines)
                    if matches:
                        findings[path] = matches

    with open("magic_numbers_report.txt", "w", encoding="utf-8") as out:
        for path, matches in findings.items():
            if matches:
                out.write(f"\n--- {os.path.basename(path)} ---\n")
                out.write(f"Total instances found: {len(matches)}\n")
                for line_num, text in matches[:10]:
                    out.write(f"L{line_num}: {text[:150]}...\n")


if __name__ == "__main__":
    main()
