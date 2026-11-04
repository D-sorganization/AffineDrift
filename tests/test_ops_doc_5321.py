"""Operations doc contract for #5321."""

from __future__ import annotations

from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "docs" / "operations"


def test_doc_exists() -> None:
    text = (OPS / "static-publishing-hardening.md").read_text(encoding="utf-8")
    assert "5318" in text
