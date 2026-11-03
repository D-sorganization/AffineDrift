"""Operations doc contract for #5318."""

from __future__ import annotations

from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "docs" / "operations"


def test_site_release_rollback_doc_exists() -> None:
    text = (OPS / "site-release-rollback.md").read_text(encoding="utf-8")
    assert "deploy-website.yml" in text
    assert "#5321" in text
