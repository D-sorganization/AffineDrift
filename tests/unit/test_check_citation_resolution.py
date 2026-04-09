"""Tests for scripts/check_citation_resolution.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_citation_resolution import (
    collect_citation_keys,
    find_citation_violations,
    resolve_bibliography_paths,
)


def test_collect_citation_keys_excludes_quarto_cross_references() -> None:
    text = """
---
title: Example
---

See @eq-motion, @sec-summary, @app-proof, and @subsec-notes for structure.
This paragraph cites [@slotine1991applied; @lohmiller1998contraction].
Narrative citations like @boyd1994 and negative cites like -@doe2023 should also count.
Chapter labels like @ch03_numerical must be ignored.
Inline code `@jax.custom_vjp` and fenced decorators must be ignored.

```python
@jit
def solve():
    return None
```
"""
    assert collect_citation_keys(text) == {
        "doe2023",
        "boyd1994",
        "lohmiller1998contraction",
        "slotine1991applied",
    }


def test_resolve_bibliography_paths_uses_nearest_project_and_frontmatter(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / "_quarto.yml").write_text("bibliography: references/root.bib\n", encoding="utf-8")

    book_dir = repo_root / "articles" / "book"
    chapter_dir = book_dir / "chapters"
    chapter_dir.mkdir(parents=True)
    (book_dir / "_quarto.yml").write_text("bibliography: references/book.bib\n", encoding="utf-8")

    chapter = chapter_dir / "01-intro.qmd"
    chapter.write_text(
        "---\n" "bibliography: chapter.bib\n" "---\n" "See [@local2026].\n",
        encoding="utf-8",
    )

    assert resolve_bibliography_paths(chapter, repo_root) == (
        (book_dir / "references" / "book.bib").resolve(),
        (chapter_dir / "chapter.bib").resolve(),
    )


def test_find_citation_violations_reports_unresolved_keys_and_missing_bibliography(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path
    (repo_root / "_quarto.yml").write_text("bibliography: references/root.bib\n", encoding="utf-8")
    (repo_root / "references").mkdir()
    (repo_root / "references" / "root.bib").write_text(
        "@article{slotine1991applied,\n  title={Applied Nonlinear Control}\n}\n",
        encoding="utf-8",
    )

    pages_dir = repo_root / "pages"
    pages_dir.mkdir()
    page = pages_dir / "example.qmd"
    page.write_text(
        "---\n"
        "bibliography:\n"
        "  - missing.bib\n"
        "---\n"
        "See @eq-motion and [@slotine1991applied; @missing2026].\n",
        encoding="utf-8",
    )

    violations = find_citation_violations(repo_root)
    assert len(violations) == 1
    violation = violations[0]
    assert violation.document == Path("pages/example.qmd")
    assert violation.missing_bibliographies == (Path("pages/missing.bib"),)
    assert violation.unresolved_keys == ("missing2026",)
