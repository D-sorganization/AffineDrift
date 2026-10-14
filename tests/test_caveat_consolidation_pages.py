"""Tests for caveat consolidation on core pages (#4589)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.caveats_block import validate_caveats_dict
from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[1]
CONSOLIDATED_PAGES = ["pages/tools.qmd", "pages/big-idea.qmd", "pages/how-to-read.qmd"]


@pytest.mark.parametrize("rel_path", CONSOLIDATED_PAGES)
def test_consolidated_page_has_valid_structured_caveats(rel_path: str) -> None:
    """Verify that consolidated pages define schema-valid caveats front matter."""
    full_path = ROOT / rel_path
    assert full_path.is_file()
    fm, _ = split_frontmatter(full_path.read_text(encoding="utf-8"))
    assert "caveats" in fm
    errs = validate_caveats_dict(fm["caveats"])
    assert not errs, f"{rel_path} caveats invalid: {errs}"
