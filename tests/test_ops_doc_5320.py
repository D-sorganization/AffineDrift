"""Operations doc contract for #5320."""

from __future__ import annotations

from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "docs" / "operations"


def test_doc_exists() -> None:
    text = (OPS / "post-deploy-verification.md").read_text(encoding="utf-8")
    assert "post_render_sri_audit" in text
