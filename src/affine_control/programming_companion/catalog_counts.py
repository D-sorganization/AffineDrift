"""Derive program inventory counts from committed programming companion QMD pages."""

from __future__ import annotations

import re

PROGRAM_REGISTRY_HEADING_RE = re.compile(
    r"^## Program Registry \((\d+) Records\)\s*$",
    re.MULTILINE,
)
INDEX_PROGRAM_CARD_RE = re.compile(r"Programs and Models \((\d+)\)")
INDEX_PROGRAM_BLURB_RE = re.compile(r"full (\d+)-record program")
PROGRAMS_DESCRIPTION_RE = re.compile(
    r'^description: "Authoritative inventory of (\d+) UpstreamDrift', re.MULTILINE
)
ON_RAMP_BLURB_RE = re.compile(r"from the (\d+)-record directory")


def count_program_registry_table_rows(markdown: str) -> int:
    """Count data rows in the programs registry pipe table."""
    count = 0
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        count += 1
    return count


def _single_match(pattern: re.Pattern[str], text: str, label: str) -> int:
    """Return the sole integer captured by ``pattern`` in ``text`` or raise ``ValueError``."""
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label} count in source, found {len(matches)}")
    return int(matches[0])


def committed_program_registry_count(programs_qmd: str) -> int:
    """Return the authoritative program count from the registry page."""
    table_count = count_program_registry_table_rows(programs_qmd)
    heading_count = _single_match(PROGRAM_REGISTRY_HEADING_RE, programs_qmd, "registry heading")
    description_count = _single_match(PROGRAMS_DESCRIPTION_RE, programs_qmd, "registry description")
    if table_count != heading_count or table_count != description_count:
        msg = (
            f"programs.qmd program counts disagree: table={table_count}, "
            f"heading={heading_count}, description={description_count}"
        )
        raise ValueError(msg)
    return table_count


def committed_program_hub_counts(index_qmd: str) -> tuple[int, int]:
    """Return the card title and blurb counts from the programming hub index."""
    title_count = _single_match(INDEX_PROGRAM_CARD_RE, index_qmd, "hub card title")
    blurb_count = _single_match(INDEX_PROGRAM_BLURB_RE, index_qmd, "hub card blurb")
    return title_count, blurb_count
