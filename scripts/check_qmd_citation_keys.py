#!/usr/bin/env python3
"""Validate that Quarto website citations resolve against configured bibliographies."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import yaml

from src.tools.reference_audit import parse_bibtex_entry_keys

logger = logging.getLogger(__name__)

QMD_CITATION_PATTERN = re.compile(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9:_-]*)")
FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FENCED_CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
IGNORED_CITATION_PREFIXES = (
    "app:",
    "ch:",
    "ch-",
    "def:",
    "eq:",
    "eq-",
    "fig:",
    "fig-",
    "lem:",
    "prop:",
    "sec:",
    "sec-",
    "subsec:",
    "tab:",
    "tbl:",
    "thm:",
)
IGNORED_CITATION_PATTERNS = (
    re.compile(r"^ch\d+[_-]"),
)


def extract_frontmatter(text: str) -> dict:
    """Return parsed YAML frontmatter when present."""
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}
    payload = yaml.safe_load(match.group(1)) or {}
    if not isinstance(payload, dict):
        return {}
    return payload


def extract_citation_keys(text: str) -> set[str]:
    """Return the set of bibliography citation keys referenced in QMD text."""
    text = FENCED_CODE_BLOCK_PATTERN.sub("", text)
    text = INLINE_CODE_PATTERN.sub("", text)
    keys = {
        match.group(1)
        for match in QMD_CITATION_PATTERN.finditer(text)
        if not match.group(1).startswith(IGNORED_CITATION_PREFIXES)
        and not any(pattern.match(match.group(1)) for pattern in IGNORED_CITATION_PATTERNS)
    }
    return keys


def normalize_bibliography_value(value: object) -> list[str]:
    """Normalize Quarto bibliography config to a list of relative paths."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def configured_bibliography_paths(repo_root: Path, qmd_path: Path) -> list[Path]:
    """Resolve bibliography files configured for a given QMD document."""
    resolved: list[Path] = []
    seen: set[Path] = set()

    def add_paths(base_dir: Path, value: object) -> None:
        for rel_path in normalize_bibliography_value(value):
            path = (base_dir / rel_path).resolve()
            if path not in seen and path.exists():
                seen.add(path)
                resolved.append(path)

    text = qmd_path.read_text(encoding="utf-8")
    add_paths(qmd_path.parent, extract_frontmatter(text).get("bibliography"))

    for parent in [qmd_path.parent, *qmd_path.parents]:
        if parent == repo_root.parent:
            break
        quarto_config = parent / "_quarto.yml"
        if quarto_config.exists():
            config = yaml.safe_load(quarto_config.read_text(encoding="utf-8")) or {}
            if isinstance(config, dict):
                add_paths(parent, config.get("bibliography"))
        if parent == repo_root:
            break

    return resolved


def load_bibliography_keys(path: Path) -> set[str]:
    """Load citation keys from a bibliography file."""
    if path.suffix == ".bib":
        return parse_bibtex_entry_keys(path.read_text(encoding="utf-8"))
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return {
                entry["id"]
                for entry in payload
                if isinstance(entry, dict) and isinstance(entry.get("id"), str)
            }
    return set()


def iter_qmd_files(repo_root: Path) -> list[Path]:
    """Collect all website QMD files subject to citation validation."""
    roots = [
        repo_root / "articles",
        repo_root / "books",
        repo_root / "pages",
        repo_root / "resources",
    ]
    qmd_files: list[Path] = [repo_root / "index.qmd"]
    for root in roots:
        if root.exists():
            qmd_files.extend(path for path in root.rglob("*.qmd"))
    return sorted(path for path in qmd_files if path.exists())


def find_unresolved_citations(repo_root: Path) -> list[str]:
    """Return unresolved citation diagnostics for all configured QMD files."""
    diagnostics: list[str] = []
    for qmd_path in iter_qmd_files(repo_root):
        content = qmd_path.read_text(encoding="utf-8")
        citation_keys = extract_citation_keys(content)
        if not citation_keys:
            continue

        bibliography_paths = configured_bibliography_paths(repo_root, qmd_path)
        if not bibliography_paths:
            diagnostics.append(f"{qmd_path.relative_to(repo_root)}: citations present but no bibliography configured")
            continue

        available_keys: set[str] = set()
        for bib_path in bibliography_paths:
            available_keys.update(load_bibliography_keys(bib_path))

        missing = sorted(key for key in citation_keys if key not in available_keys)
        if missing:
            diagnostics.append(
                f"{qmd_path.relative_to(repo_root)}: unresolved citation keys: {', '.join(missing)}"
            )
    return diagnostics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root containing articles/, books/, pages/, resources/, and index.qmd",
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    repo_root = args.repo_root.resolve()
    unresolved = find_unresolved_citations(repo_root)
    if unresolved:
        logger.error("Unresolved Quarto citation keys detected:")
        for diagnostic in unresolved:
            logger.error("  %s", diagnostic)
        return 1

    logger.info("Quarto citation integrity check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
