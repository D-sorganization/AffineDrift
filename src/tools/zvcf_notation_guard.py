"""Detect retired ZVCF definitions that contradict NOTATION.md (#5588)."""

from __future__ import annotations

import re
from pathlib import Path

SEARCH_ROOTS = ("articles", "books", "content", "data/trust", "pages")
ROOT_FILES = ("NOTATION.md",)
SUFFIXES = {".tex", ".qmd", ".md", ".json"}
GENERATED_PREFIXES = (
    "articles/_generated/",
    "_includes/generated/",
)

LEGACY_ZVCF_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        r"hold a position still",
        "legacy holding-torque ZVCF summary",
    ),
    (
        r"a_\{\\mathrm\{ZVCF\}\}=a_0\(q,0\)=-M\(q\)\^\{-1\}g_q\(q\)",
        "ZVCF as zero-input gravity acceleration",
    ),
    (
        r"a_\{\\mathrm\{ZVCF\}\}\(z\)=-M\(z\)\^\{-1\}h\(z,0\)",
        "ZVCF as zero-velocity zero-control acceleration",
    ),
    (
        r"both velocity and declared control set to zero",
        "ZVCF defined with u=0",
    ),
    (
        r"a_\{\\mathrm\{ZVCF\}\}\(q,z\)=-M\(q\)\^\{-1\}h\(q,0",
        "ZVCF as configuration bias acceleration",
    ),
    (
        r"evaluates that model at a specified velocity-reset state",
        "ZVCF mislabeled as velocity-reset state evaluation",
    ),
)

_COMPILED = tuple((re.compile(pat), label) for pat, label in LEGACY_ZVCF_PATTERNS)


def _is_generated(relative: str) -> bool:
    """Return whether ``relative`` points at a generated mirror path."""
    return any(relative.startswith(prefix) for prefix in GENERATED_PREFIXES)


def iter_zvcf_guarded_sources(root: Path) -> list[Path]:
    """Content sources scanned for legacy ZVCF wording (excludes generated mirrors)."""
    found: list[Path] = []
    for name in SEARCH_ROOTS:
        directory = root / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.suffix not in SUFFIXES:
                continue
            rel = path.relative_to(root).as_posix()
            if _is_generated(rel):
                continue
            found.append(path)
    for name in ROOT_FILES:
        path = root / name
        if path.is_file():
            found.append(path)
    return sorted(set(found))


def scan_legacy_zvcf_definitions(
    root: Path,
    *,
    paths: tuple[Path, ...] | None = None,
) -> list[dict[str, object]]:
    """Return one finding dict per legacy pattern match."""
    targets = list(paths) if paths is not None else iter_zvcf_guarded_sources(root)
    findings: list[dict[str, object]] = []
    for path in targets:
        relative = path.relative_to(root).as_posix()
        if _is_generated(relative):
            continue
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, label in _COMPILED:
                if pattern.search(line):
                    findings.append(
                        {
                            "file": relative,
                            "line": number,
                            "pattern": label,
                            "text": line.strip(),
                        }
                    )
    return findings
