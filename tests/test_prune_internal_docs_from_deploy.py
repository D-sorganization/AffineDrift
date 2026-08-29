"""Tests for scripts/prune_internal_docs_from_deploy.py."""

from __future__ import annotations

from pathlib import Path

from scripts.prune_internal_docs_from_deploy import (
    prune_internal_deploy_artifacts,
    prune_internal_markdown_files,
    strip_legacy_math_polyfill,
)


def test_prune_internal_markdown_files_removes_md_only(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.html").write_text("<h1>Home</h1>", encoding="utf-8")
    (docs / "styles.css").write_text("body {}", encoding="utf-8")
    (docs / "GOVERNANCE.md").write_text("# Governance", encoding="utf-8")

    sub = docs / "operations"
    sub.mkdir()
    (sub / "runbook.md").write_text("# Runbook", encoding="utf-8")
    (sub / "report.html").write_text("<h1>Report</h1>", encoding="utf-8")

    deleted = prune_internal_markdown_files(docs)

    assert len(deleted) == 2
    assert not (docs / "GOVERNANCE.md").exists()
    assert not (sub / "runbook.md").exists()
    assert (docs / "index.html").exists()
    assert (docs / "styles.css").exists()
    assert (sub / "report.html").exists()


def test_prune_internal_markdown_files_handles_missing_dir(tmp_path: Path):
    non_existent = tmp_path / "non_existent"
    deleted = prune_internal_markdown_files(non_existent)
    assert deleted == []


def test_prune_internal_deploy_artifacts_removes_excluded_html_trees(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    public = docs / "articles/theory-part1.html"
    draft = docs / "articles/tangent-hyperplane-articles/Drafts_Original_Articles/draft.html"
    retired = docs / "articles/tangent-hyperplane-contraction/index.html"
    for path in (public, draft, retired):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<h1>Page</h1>", encoding="utf-8")

    deleted = prune_internal_deploy_artifacts(docs)

    assert public.is_file()
    assert not draft.exists()
    assert not retired.exists()
    assert {path.name for path in deleted} == {"draft.html", "index.html"}


def test_strip_legacy_math_polyfill_preserves_local_runtime_gate(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    page = docs / "article.html"
    docs.mkdir()
    page.write_text(
        """<script src=\"https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=es6\"></script>
<script src=\"js/equation-runtime-gate.js\"></script>
<main><h1>Article</h1></main>
""",
        encoding="utf-8",
    )

    changed = strip_legacy_math_polyfill(docs)

    rendered = page.read_text(encoding="utf-8")
    assert changed == [page]
    assert "cdnjs.cloudflare.com/polyfill" not in rendered
    assert "equation-runtime-gate.js" in rendered
