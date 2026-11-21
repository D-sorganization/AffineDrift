"""Operations doc contract for #5317."""

from __future__ import annotations

from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "docs" / "operations"


def test_doc_exists() -> None:
    text = (OPS / "mobile-publication-readiness.md").read_text(encoding="utf-8")
    assert "5313" in text
