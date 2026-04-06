#!/usr/bin/env python3
"""Fail when website citations do not resolve against configured bibliographies."""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.tools.reference_audit import parse_bibtex_entry_keys

logger = logging.getLogger(__name__)

QMD_PATHS = ("articles", "books", "pages", "resources")
FRONTMATTER_DELIMITER = "---"
ENTRY_KEY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)")
CITATION_PATTERN = re.compile(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9:._/-]*)")
CROSS_REFERENCE_PREFIXES = (
    "app-",
    "app:",
    "sec-",
    "sec:",
    "subsec-",
    "subsec:",
    "fig-",
    "fig:",
    "tab-",
    "tab:",
    "tbl-",
    "tbl:",
    "eq-",
    "eq:",
    "ch-",
    "ch:",
    "q-",
    "q:",
)
CHAPTER_LABEL_PATTERN = re.compile(r"^ch\d", re.IGNORECASE)
FENCED_CODE_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`]+`")


class CitationResolutionError(Exception):
    """Raised when citation-check inputs are unreadable or malformed."""


@dataclass(frozen=True)
class CitationViolation:
    """Describe a citation-resolution problem in one source document."""

    document: Path
    missing_bibliographies: tuple[Path, ...]
    unresolved_keys: tuple[str, ...]


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file as a dictionary."""
    if path is None:
        raise CitationResolutionError("path must not be None")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise CitationResolutionError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CitationResolutionError(f"Expected mapping in {path}, got {type(data).__name__}")
    return data


def find_nearest_quarto_config(document: Path, repo_root: Path) -> Path | None:
    """Return the nearest ancestor _quarto.yml for a document."""
    for directory in (document.parent, *document.parents):
        if directory == document:
            continue
        config_path = directory / "_quarto.yml"
        if config_path.exists():
            return config_path
        if directory == repo_root:
            break
    return None


def strip_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return parsed frontmatter and body text for a qmd document."""
    if not text.startswith(f"{FRONTMATTER_DELIMITER}\n"):
        return {}, text

    parts = text.split(f"\n{FRONTMATTER_DELIMITER}\n", 1)
    if len(parts) != 2:
        return {}, text

    _, remainder = parts
    frontmatter_text = text[len(FRONTMATTER_DELIMITER) + 1 : len(text) - len(remainder) - 5]
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise CitationResolutionError("Document frontmatter must be a YAML mapping.")
    return data, remainder


def normalize_bibliography_values(value: Any) -> list[str]:
    """Normalize a bibliography field into a list of string paths."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise CitationResolutionError("bibliography must be a string or list of strings")


def resolve_bibliography_paths(document: Path, repo_root: Path) -> tuple[Path, ...]:
    """Resolve bibliography files configured for a document."""
    config_paths: list[Path] = []
    quarto_config = find_nearest_quarto_config(document, repo_root)
    if quarto_config is not None:
        config_data = load_yaml_file(quarto_config)
        config_paths.extend(
            (quarto_config.parent / rel_path).resolve()
            for rel_path in normalize_bibliography_values(config_data.get("bibliography"))
        )

    frontmatter, _ = strip_frontmatter(document.read_text(encoding="utf-8"))
    config_paths.extend(
        (document.parent / rel_path).resolve()
        for rel_path in normalize_bibliography_values(frontmatter.get("bibliography"))
    )

    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for path in config_paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)
    return tuple(unique_paths)


def load_bibliography_keys(path: Path) -> set[str]:
    """Load bibliography entry keys from a supported bibliography file."""
    if path.suffix == ".bib":
        return parse_bibtex_entry_keys(path.read_text(encoding="utf-8"))
    if path.suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise CitationResolutionError(f"Expected bibliography list in {path}")
        return {
            str(entry["id"])
            for entry in raw
            if isinstance(entry, dict) and "id" in entry and str(entry["id"]).strip()
        }
    raise CitationResolutionError(f"Unsupported bibliography format: {path}")


def is_cross_reference(key: str) -> bool:
    """Return True when the key is a Quarto internal cross-reference."""
    normalized = key.lower()
    return (
        normalized.startswith(CROSS_REFERENCE_PREFIXES)
        or CHAPTER_LABEL_PATTERN.match(normalized) is not None
    )


def collect_citation_keys(text: str) -> set[str]:
    """Extract citation keys from qmd text, excluding Quarto cross-references."""
    _, body = strip_frontmatter(text)
    body = FENCED_CODE_PATTERN.sub("", body)
    body = INLINE_CODE_PATTERN.sub("", body)
    keys = {match.group(1).rstrip(".,;:") for match in CITATION_PATTERN.finditer(body)}
    return {key for key in keys if not is_cross_reference(key)}


def iter_target_documents(repo_root: Path) -> list[Path]:
    """Return website qmd files that must pass citation resolution checks."""
    documents: list[Path] = []
    root_index = repo_root / "index.qmd"
    if root_index.exists():
        documents.append(root_index)
    for directory_name in QMD_PATHS:
        directory = repo_root / directory_name
        if not directory.exists():
            continue
        documents.extend(sorted(directory.rglob("*.qmd")))
    return documents


def find_citation_violations(repo_root: Path) -> list[CitationViolation]:
    """Collect citation violations across the website source tree."""
    violations: list[CitationViolation] = []
    for document in iter_target_documents(repo_root):
        text = document.read_text(encoding="utf-8")
        cited_keys = collect_citation_keys(text)
        bibliography_paths = resolve_bibliography_paths(document, repo_root)
        missing_bibliographies = tuple(path for path in bibliography_paths if not path.exists())

        available_keys: set[str] = set()
        for bibliography_path in bibliography_paths:
            if bibliography_path.exists():
                available_keys.update(load_bibliography_keys(bibliography_path))

        unresolved_keys = tuple(sorted(key for key in cited_keys if key not in available_keys))
        if missing_bibliographies or unresolved_keys:
            violations.append(
                CitationViolation(
                    document=document.relative_to(repo_root),
                    missing_bibliographies=tuple(
                        path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
                        for path in missing_bibliographies
                    ),
                    unresolved_keys=unresolved_keys,
                )
            )
    return violations


def format_violation(violation: CitationViolation) -> list[str]:
    """Format one violation for CLI output."""
    messages = [f"{violation.document}:"]
    for bibliography_path in violation.missing_bibliographies:
        messages.append(f"  missing bibliography file: {bibliography_path}")
    for key in violation.unresolved_keys:
        messages.append(f"  unresolved citation key: {key}")
    return messages


def main() -> int:
    """Run citation-resolution checks for website content."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    repo_root = Path(__file__).resolve().parent.parent
    violations = find_citation_violations(repo_root)

    if violations:
        logger.error(
            "Citation resolution check FAILED (%d files with violations):", len(violations)
        )
        for violation in violations:
            for message in format_violation(violation):
                logger.error("%s", message)
        return 1

    logger.info(
        "Citation resolution check passed for %d qmd files.", len(iter_target_documents(repo_root))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
