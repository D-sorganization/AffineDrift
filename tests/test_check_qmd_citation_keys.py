"""Tests for scripts/check_qmd_citation_keys.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_qmd_citation_keys import (
    configured_bibliography_paths,
    extract_citation_keys,
    find_unresolved_citations,
)


def test_extract_citation_keys_ignores_cross_references() -> None:
    text = "See [@smith2020; @jones2019] and @fig:overview plus @ch:intro and @tbl:data."
    assert extract_citation_keys(text) == {"smith2020", "jones2019"}


def test_extract_citation_keys_ignores_code_annotations() -> None:
    text = """
```python
@jit
def f():
    return "@not_a_citation"
```

Use `@custom_vjp` in code, but cite [@smith2020].
"""
    assert extract_citation_keys(text) == {"smith2020"}


def test_extract_citation_keys_ignores_chapter_cross_references() -> None:
    text = "Compare the worked example in Section @ch03_numerical and cite [@smith2020]."
    assert extract_citation_keys(text) == {"smith2020"}


def test_configured_bibliography_paths_reads_frontmatter_and_quarto(tmp_path: Path) -> None:
    repo_root = tmp_path
    article_dir = repo_root / "articles" / "demo"
    article_dir.mkdir(parents=True)
    bib = article_dir / "refs.bib"
    bib.write_text("@article{smith2020,\n  title={Demo}\n}\n", encoding="utf-8")
    (article_dir / "_quarto.yml").write_text("bibliography: refs.bib\n", encoding="utf-8")
    qmd = article_dir / "chapter.qmd"
    qmd.write_text("---\ntitle: Demo\n---\n[@smith2020]\n", encoding="utf-8")

    paths = configured_bibliography_paths(repo_root, qmd)

    assert paths == [bib.resolve()]


def test_find_unresolved_citations_reports_missing_keys(tmp_path: Path) -> None:
    repo_root = tmp_path
    article_dir = repo_root / "articles" / "demo"
    article_dir.mkdir(parents=True)
    (article_dir / "_quarto.yml").write_text("bibliography: refs.bib\n", encoding="utf-8")
    (article_dir / "refs.bib").write_text(
        "@article{smith2020,\n  title={Demo}\n}\n", encoding="utf-8"
    )
    (article_dir / "chapter.qmd").write_text(
        "[@smith2020; @missing2024; @sec:intro]\n", encoding="utf-8"
    )

    diagnostics = find_unresolved_citations(repo_root)

    assert diagnostics == ["articles/demo/chapter.qmd: unresolved citation keys: missing2024"]
