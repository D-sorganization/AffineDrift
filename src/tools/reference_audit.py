"""Reference audit helpers for Tangent-Space Methods citations."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from src.core.contracts import require

logger = logging.getLogger(__name__)

BIB_ENTRY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
CITE_PATTERN = re.compile(r"\\cite\w*\{([^}]+)\}")
DOI_PATTERN = re.compile(r"\bdoi\s*=", re.IGNORECASE)
URL_PATTERN = re.compile(r"\burl\s*=", re.IGNORECASE)
ISBN_PATTERN = re.compile(r"\bisbn\s*=", re.IGNORECASE)
ENTRY_BLOCK_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.IGNORECASE | re.DOTALL)


def parse_bibtex_entry_keys(bib_text: str) -> set[str]:
    """Extract citation keys from BibTeX entry declarations."""
    require(len(bib_text) > 0, "bib_text must not be empty")
    return {match.group(1).strip() for match in BIB_ENTRY_PATTERN.finditer(bib_text)}


def collect_citation_keys_from_tex(tex_text: str) -> set[str]:
    """Extract citation keys from TeX cite-like commands."""
    require(len(tex_text) > 0, "tex_text must not be empty")
    keys: set[str] = set()
    for match in CITE_PATTERN.finditer(tex_text):
        raw_group = match.group(1)
        keys.update(part.strip() for part in raw_group.split(",") if part.strip())
    return keys


def validate_bibtex_identifier_fields(bib_text: str) -> list[str]:
    """Validate each BibTeX entry has DOI, URL, or ISBN metadata."""
    require(len(bib_text) > 0, "bib_text must not be empty")
    errors: list[str] = []
    for match in ENTRY_BLOCK_PATTERN.finditer(bib_text):
        key = match.group(1).strip()
        block = match.group(2)
        has_identifier = any(
            pattern.search(block) for pattern in (DOI_PATTERN, URL_PATTERN, ISBN_PATTERN)
        )
        if not has_identifier:
            errors.append(f"{key}: missing DOI/URL/ISBN identifier")
    return errors


def load_text(path: Path) -> str:
    """Load UTF-8 text from disk with existence precondition."""
    require(path.exists(), f"Missing file: {path}")
    return path.read_text(encoding="utf-8")
