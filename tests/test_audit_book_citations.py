"""Unit and regression tests for scripts/audit_book_citations.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_book_citations import (
    audit_book_citations,
    audit_chapter_citations,
    extract_sentences,
    format_markdown_report,
    main,
    normalize_words,
    parse_latex_citations,
    parse_quarto_citations,
)


def create_synthetic_citation_tree(
    root: Path,
    book_key: str,
    tex_files: dict[str, str],
    qmd_files: dict[str, str],
) -> tuple[Path, Path]:
    """Build a mock directory tree for testing citation parity."""
    tex_dir = root / f"articles/{book_key}/chapters"
    qmd_dir = root / f"articles/{book_key}/quarto"
    tex_dir.mkdir(parents=True, exist_ok=True)
    qmd_dir.mkdir(parents=True, exist_ok=True)

    for stem, content in tex_files.items():
        (tex_dir / f"{stem}.tex").write_text(content, encoding="utf-8")
    for stem, content in qmd_files.items():
        (qmd_dir / f"{stem}.qmd").write_text(content, encoding="utf-8")

    return tex_dir, qmd_dir


class TestCitationParsing:
    """Test extraction of citation keys from LaTeX and Quarto sources."""

    def test_parse_latex_citations_standard_and_bracketed(self) -> None:
        tex = r"""
The double pendulum model \citep{Jorgensen1994,Penner2001} provides foundational insights.
As noted by \citet{Nesbit2005}, the shoulder torque reaches peak values early.
Also see \cite{Gatt1998}.
"""
        keys, occurrences = parse_latex_citations(tex)
        assert keys == {"Jorgensen1994", "Penner2001", "Nesbit2005", "Gatt1998"}
        assert len(occurrences) == 3

    def test_parse_quarto_citations_standard_and_bracketed(self) -> None:
        qmd = """
The double pendulum model [@Jorgensen1994; @Penner2001] provides foundational insights.
As noted by @Nesbit2005, the shoulder torque reaches peak values early.
Cross references like @fig-double_pendulum and @sec-forces should be ignored.
"""
        keys = parse_quarto_citations(qmd)
        assert keys == {"Jorgensen1994", "Penner2001", "Nesbit2005"}
        assert "fig-double_pendulum" not in keys
        assert "sec-forces" not in keys

    def test_sentence_extraction_and_normalization(self) -> None:
        raw = "The ground reaction force is $F_z = mg$! It drives motion."
        sentences = extract_sentences(raw)
        assert len(sentences) == 2
        norm = normalize_words(sentences[0])
        assert norm == "the ground reaction force is f z mg"


class TestCitationAuditExecution:
    """Test chapter and book-level citation parity audits."""

    def test_audit_chapter_citations_matches(self, tmp_path: Path) -> None:
        tex = r"The swing dynamics were modeled by \citet{Jorgensen1994} and \citep{Penner2001}."
        qmd = "The swing dynamics were modeled by @Jorgensen1994 and [@Penner2001]."
        tex_dir, qmd_dir = create_synthetic_citation_tree(
            tmp_path,
            "test_book",
            {"ch01": tex},
            {"ch01": qmd},
        )
        audit = audit_chapter_citations(
            tex_path=tex_dir / "ch01.tex",
            qmd_path=qmd_dir / "ch01.qmd",
        )
        assert set(audit.tex_unique_keys) == {"Jorgensen1994", "Penner2001"}
        assert set(audit.qmd_unique_keys) == {"Jorgensen1994", "Penner2001"}
        assert set(audit.shared_keys) == {"Jorgensen1994", "Penner2001"}
        assert set(audit.book_only_keys) == set()
        assert set(audit.mirror_only_keys) == set()
        assert audit.mechanical_restoration_candidates == 0

    def test_audit_chapter_citations_identifies_missing_candidate(self, tmp_path: Path) -> None:
        tex = r"The swing dynamics were modeled by \citet{Jorgensen1994} in detail."
        qmd = "The swing dynamics were modeled by researchers in detail."
        tex_dir, qmd_dir = create_synthetic_citation_tree(
            tmp_path,
            "test_book",
            {"ch01": tex},
            {"ch01": qmd},
        )
        audit = audit_chapter_citations(
            tex_path=tex_dir / "ch01.tex",
            qmd_path=qmd_dir / "ch01.qmd",
            similarity_threshold=0.70,
        )
        assert set(audit.book_only_keys) == {"Jorgensen1994"}
        assert audit.mechanical_restoration_candidates == 1

    def test_format_markdown_report_structure(self, tmp_path: Path) -> None:
        tex = r"\cite{Penner2001}"
        qmd = "[@Penner2001]"
        create_synthetic_citation_tree(
            tmp_path,
            "test_book",
            {"ch01": tex},
            {"ch01": qmd},
        )
        book_audit = audit_book_citations(tmp_path / "articles/test_book")
        md = format_markdown_report(book_audit)
        assert "# Citations Parity Audit" in md
        assert "Total Unique Keys in LaTeX Book" in md
        assert "`ch01`" in md

    def test_main_cli_json_and_markdown(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        tex = r"\cite{Penner2001}"
        qmd = "[@Penner2001]"
        create_synthetic_citation_tree(
            tmp_path,
            "The_Physics_of_Golf",
            {"ch01_test": tex},
            {"ch01_test": qmd},
        )
        ret = main(["--book", str(tmp_path / "articles/The_Physics_of_Golf"), "--json"])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["book_title"] == "The_Physics_of_Golf"
        assert len(data["chapters"]) == 1
