"""Forward Dynamics Matching book uses chapter H1 titles during schema migration (#4949)."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_frontmatter import validate_file
from src.tools.utils.frontmatter_schema import ALLOWLIST_PATH, load_frontmatter_allowlist

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"


def test_forward_dynamics_matching_chapters_are_allowlisted() -> None:
    """Book chapters defer full article schema until publication metadata is drafted."""
    cfg = load_frontmatter_allowlist(ALLOWLIST_PATH)
    allowlisted = set(cfg["allowlist"])
    chapters = sorted(BOOK_DIR.glob("*.qmd"))
    assert chapters, "expected Forward Dynamics Matching Quarto chapters"
    missing = [
        p.relative_to(REPO_ROOT).as_posix()
        for p in chapters
        if p.relative_to(REPO_ROOT).as_posix() not in allowlisted
    ]
    assert not missing, f"chapters missing from article-front-matter allowlist: {missing}"


def test_forward_dynamics_matching_passes_frontmatter_gate() -> None:
    """CI static-check frontmatter validation must pass for the recovered book."""
    for qmd in sorted(BOOK_DIR.glob("*.qmd")):
        errors = validate_file(qmd)
        assert not errors, f"{qmd.relative_to(REPO_ROOT)}: {errors}"
