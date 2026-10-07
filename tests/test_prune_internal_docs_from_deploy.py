"""Tests for scripts/prune_internal_docs_from_deploy.py."""

from __future__ import annotations

from pathlib import Path

from scripts.prune_internal_docs_from_deploy import (
    prune_internal_deploy_artifacts,
    strip_legacy_math_polyfill,
)


def test_prune_internal_deploy_artifacts_leaves_markdown_alone(tmp_path: Path) -> None:
    """Issue #4597: Quarto no longer renders into the tracked docs/ directory,
    so raw markdown never lands in the deploy artifact. Pruning it is no
    longer this script's job.
    """
    docs = tmp_path / "_site"
    docs.mkdir()
    (docs / "index.html").write_text("<h1>Home</h1>", encoding="utf-8")
    (docs / "GOVERNANCE.md").write_text("# Governance", encoding="utf-8")

    deleted = prune_internal_deploy_artifacts(docs)

    assert (docs / "GOVERNANCE.md").exists()
    assert (docs / "index.html").exists()
    assert deleted == []


def test_prune_internal_deploy_artifacts_removes_excluded_html_trees(tmp_path: Path) -> None:
    docs = tmp_path / "_site"
    public = docs / "articles/theory-part1.html"
    draft = docs / "articles/tangent-hyperplane-articles/Drafts_Original_Articles/draft.html"
    retired = docs / "articles/tangent-hyperplane-contraction/index.html"
    wrist_claude = docs / "content/wrist-as-universal-joint/Wrist_Universal_Claude.html"
    for path in (public, draft, retired, wrist_claude):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<h1>Page</h1>", encoding="utf-8")

    deleted = prune_internal_deploy_artifacts(docs)

    assert public.is_file()
    assert not draft.exists()
    assert not retired.exists()
    assert not wrist_claude.exists()
    assert {path.name for path in deleted} == {
        "draft.html",
        "index.html",
        "Wrist_Universal_Claude.html",
    }


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
