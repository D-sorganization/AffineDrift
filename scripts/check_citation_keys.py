#!/usr/bin/env python3
"""Check that every Quarto citation key in website source files resolves to a bibliography entry.

Scans .qmd files under articles/, books/, pages/, resources/, and index.qmd.
For each Quarto book project the bibliography is determined from the project's
_quarto.yml (``bibliography:`` field).  For standalone .qmd files that declare
``bibliography:`` in their own YAML front-matter that file is used instead.
When no bibliography is declared the repository-wide ``references/affine-drift.bib``
is used as a fallback.

Quarto internal cross-references of the form ``@sec-``, ``@eq-``, ``@fig-``,
``@tbl-``, ``@ch-``, ``@lst-``, ``@thm-``, ``@cor-``, ``@def-``, ``@exm-``,
and ``@exr-`` are excluded from the check.

Exits 0 when all keys resolve, 1 when any are unresolved.

Closes issue #2224.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── patterns ────────────────────────────────────────────────────────────────

# Matches citation blocks like [@key], [@key1; @key2], [-@key], etc.
# First pattern captures the opening [@key] or [-@key] form.
# Second pattern captures additional @key entries within the same bracket group.
_CITE_BLOCK_RE = re.compile(r"\[(-?@[^\]]+)\]")
_CITE_KEY_RE = re.compile(r"@([^\];,\s@\]]+)")

# Quarto internal cross-reference prefixes to skip.
# Quarto supports both hyphenated (@sec-label) and colon-separated (@sec:label) forms.
_INTERNAL_PREFIXES = (
    "sec-",
    "sec:",
    "eq-",
    "eq:",
    "fig-",
    "fig:",
    "tbl-",
    "tbl:",
    "ch-",
    "ch:",
    "lst-",
    "lst:",
    "thm-",
    "thm:",
    "cor-",
    "cor:",
    "def-",
    "def:",
    "exm-",
    "exm:",
    "exr-",
    "exr:",
)

# BibTeX entry key extractor
_BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)

# YAML bibliography field in front-matter or _quarto.yml
_YAML_BIB_RE = re.compile(r"^bibliography\s*:\s*(.+)$", re.MULTILINE)


# ─── bibliography helpers ────────────────────────────────────────────────────


def parse_bib_keys(bib_path: Path) -> set[str]:
    """Return the set of citation keys declared in a .bib file."""
    if not bib_path.exists():
        logger.warning("Bibliography not found: %s", bib_path)
        return set()
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    return {m.group(1).strip() for m in _BIB_KEY_RE.finditer(text)}


def _resolve_bib_path(declared: str, base: Path) -> Path:
    """Resolve a ``bibliography:`` value relative to *base* directory."""
    return (base / declared.strip()).resolve()


def find_project_bib(qmd_path: Path, repo_root: Path) -> Path | None:
    """Return the bibliography file for a .qmd file.

    Search order:
    1. ``bibliography:`` in the file's own YAML front-matter (highest priority).
    2. Nearest non-root ``_quarto.yml`` above the file (within repo, excluding root).
    3. Root ``_quarto.yml`` (lowest priority — site-wide default).
    4. None (caller should use the fallback).

    Per-file front-matter takes priority because sub-projects such as
    tangent-hyperplane-contraction chapters declare their own bibliography
    path that overrides the site-wide _quarto.yml setting.
    """
    # 1. Per-file YAML front-matter
    try:
        text = qmd_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            front_matter = text[3:end]
            m = _YAML_BIB_RE.search(front_matter)
            if m:
                candidate = _resolve_bib_path(m.group(1), qmd_path.parent)
                if candidate.exists():
                    return candidate

    # 2 & 3. Walk up for _quarto.yml, skipping root
    repo_root_resolved = repo_root.resolve()
    current = qmd_path.parent
    while True:
        quarto_yml = current / "_quarto.yml"
        if quarto_yml.exists():
            yml_text = quarto_yml.read_text(encoding="utf-8", errors="replace")
            m = _YAML_BIB_RE.search(yml_text)
            if m:
                return _resolve_bib_path(m.group(1), current)
        if current.resolve() == repo_root_resolved or current.parent == current:
            break
        current = current.parent

    return None


# ─── citation extraction ─────────────────────────────────────────────────────


def _strip_code_and_yaml(text: str) -> str:
    """Remove fenced code blocks and YAML front-matter from text."""
    # Strip YAML front-matter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]

    # Strip fenced code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Strip inline code (`...`)
    text = re.sub(r"`[^`]*`", "", text)
    return text


def extract_citation_keys(qmd_text: str) -> set[str]:
    """Extract Quarto citation keys from a .qmd file, excluding internal refs.

    Handles single-key ([@key]) and multi-key ([@key1; @key2]) citation groups,
    as well as the author-suppressed form ([-@key]).
    """
    cleaned = _strip_code_and_yaml(qmd_text)
    keys: set[str] = set()
    for block_m in _CITE_BLOCK_RE.finditer(cleaned):
        block = block_m.group(1)
        for key_m in _CITE_KEY_RE.finditer(block):
            key = key_m.group(1).strip()
            if any(key.startswith(prefix) for prefix in _INTERNAL_PREFIXES):
                continue
            keys.add(key)
    return keys


# ─── file discovery ──────────────────────────────────────────────────────────

_SCAN_DIRS = ("articles", "books", "pages", "resources")
_SCAN_ROOT_FILES = ("index.qmd",)


def find_qmd_files(repo_root: Path) -> list[Path]:
    """Return all .qmd files in the configured scan scope."""
    found: list[Path] = []
    for name in _SCAN_ROOT_FILES:
        p = repo_root / name
        if p.exists():
            found.append(p)
    for dir_name in _SCAN_DIRS:
        d = repo_root / dir_name
        if not d.exists():
            continue
        for p in d.rglob("*.qmd"):
            found.append(p)
    return sorted(found)


# ─── main check ──────────────────────────────────────────────────────────────


def check_citations(repo_root: Path) -> list[str]:
    """Return a list of violation messages for unresolved citation keys."""
    fallback_bib = repo_root / "references" / "affine-drift.bib"
    fallback_keys = parse_bib_keys(fallback_bib)

    # Cache bib → keys to avoid re-parsing the same file many times
    bib_cache: dict[Path, set[str]] = {fallback_bib: fallback_keys}

    violations: list[str] = []
    qmd_files = find_qmd_files(repo_root)
    logger.info("Scanning %d .qmd files for citation key resolution...", len(qmd_files))

    for qmd_path in qmd_files:
        try:
            text = qmd_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            logger.warning("Cannot read %s", qmd_path)
            continue

        keys = extract_citation_keys(text)
        if not keys:
            continue

        bib_path = find_project_bib(qmd_path, repo_root)
        if bib_path is None:
            bib_path = fallback_bib

        if bib_path not in bib_cache:
            bib_cache[bib_path] = parse_bib_keys(bib_path)
        available_keys = bib_cache[bib_path]

        # Also accept keys from the fallback (affine-drift.bib) for any file
        combined_keys = available_keys | fallback_keys

        rel_path = qmd_path.relative_to(repo_root)
        for key in sorted(keys):
            if key not in combined_keys:
                violations.append(f"{rel_path}: unresolved citation key '@{key}'")

    return violations


def main() -> int:
    """Run citation key resolution check and exit with appropriate code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo_root = Path(__file__).resolve().parent.parent

    violations = check_citations(repo_root)

    if violations:
        logger.error("Citation key check FAILED (%d unresolved keys):", len(violations))
        for v in violations:
            logger.error("  %s", v)
        return 1

    logger.info("Citation key check passed — all keys resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
