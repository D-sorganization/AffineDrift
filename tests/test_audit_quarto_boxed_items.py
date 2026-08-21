"""Unit and regression tests for scripts/audit_quarto_boxed_items.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_quarto_boxed_items import (
    audit_book_boxed_items,
    audit_chapter_boxed_items,
    compute_ngrams,
    count_quarto_callouts,
    format_markdown_report,
    main,
    parse_balanced_latex_arg,
    parse_boxed_items_from_tex,
    strip_latex_comments,
    tokenize_words,
)


def create_synthetic_box_tree(
    root: Path,
    book_key: str,
    tex_files: dict[str, str],
    qmd_files: dict[str, str],
) -> tuple[Path, Path]:
    """Build a mock directory tree for testing boxed items parity."""
    tex_dir = root / f"articles/{book_key}/chapters"
    qmd_dir = root / f"articles/{book_key}/quarto"
    tex_dir.mkdir(parents=True, exist_ok=True)
    qmd_dir.mkdir(parents=True, exist_ok=True)

    for stem, content in tex_files.items():
        (tex_dir / f"{stem}.tex").write_text(content, encoding="utf-8")
    for stem, content in qmd_files.items():
        (qmd_dir / f"{stem}.qmd").write_text(content, encoding="utf-8")

    return tex_dir, qmd_dir


class TestLatexCommentStripping:
    """Test LaTeX comment stripping."""

    def test_strips_comments_preserving_escaped_percent(self) -> None:
        raw = "Text before % comment\n100\\% real text % another comment"
        cleaned = strip_latex_comments(raw)
        assert "% comment" not in cleaned
        assert r"100\% real text" in cleaned


class TestBalancedBraceArgExtraction:
    """Test extraction of arguments with balanced braces."""

    def test_extracts_simple_arg(self) -> None:
        raw = "{Simple caption} extra"
        arg, next_pos = parse_balanced_latex_arg(raw, 0)
        assert arg == "Simple caption"
        assert next_pos == len("{Simple caption}")

    def test_extracts_nested_brace_arg(self) -> None:
        raw = r"{Force $\bm{F}_{c}$ at joint \label{fig:joint}} next"
        arg, _ = parse_balanced_latex_arg(raw, 0)
        assert arg == r"Force $\bm{F}_{c}$ at joint \label{fig:joint}"


class TestTokenizationAndContainment:
    """Test tokenization and n-gram containment calculation."""

    def test_tokenize_words_strips_latex_and_punctuation(self) -> None:
        raw = "The ground reaction force (GRF) is $F_z = m(g + a)$!"
        tokens = tokenize_words(raw)
        assert "ground" in tokens
        assert "reaction" in tokens
        assert "force" in tokens
        assert "grf" in tokens

    def test_ngram_containment_exact_match(self) -> None:
        body = "The ground reaction force is the primary external force driving pelvis rotation."
        target = "Here we see that the ground reaction force is the primary external force driving pelvis rotation during downswing."
        b_words = tokenize_words(body)
        t_words = tokenize_words(target)
        b_ngrams = compute_ngrams(b_words, n=5)
        t_ngrams = compute_ngrams(t_words, n=5)
        overlap = len(b_ngrams.intersection(t_ngrams))
        ratio = overlap / len(b_ngrams)
        assert ratio >= 0.9

    def test_ngram_containment_absent(self) -> None:
        body = "Quantum entanglement governs the microscopic spin of electron orbitals in solid states."
        target = "The double pendulum model uses Lagrangian mechanics with shoulder and wrist coordinates."
        b_words = tokenize_words(body)
        t_words = tokenize_words(target)
        b_ngrams = compute_ngrams(b_words, n=5)
        t_ngrams = compute_ngrams(t_words, n=5)
        overlap = len(b_ngrams.intersection(t_ngrams))
        ratio = overlap / len(b_ngrams)
        assert ratio == 0.0


class TestLatexBoxExtraction:
    """Test parsing of various LaTeX boxed environments."""

    def test_extracts_principle_and_definition_boxes(self) -> None:
        tex = r"""
\begin{principle}{Drift Dominance}{prin:drift_dom}
Drift forces exceed active muscular forces by a substantial factor during release.
\end{principle}

\begin{definition}{Center of Pressure}{def:cop}
The center of pressure is the instantaneous centroid of vertical force.
\end{definition}
"""
        boxes = parse_boxed_items_from_tex(tex)
        assert len(boxes) == 2
        assert boxes[0]["env"] == "principle"
        assert boxes[0]["title"] == "Drift Dominance"
        assert "Drift forces exceed" in boxes[0]["body"]
        assert boxes[1]["env"] == "definition"
        assert boxes[1]["title"] == "Center of Pressure"


class TestQuartoCalloutExtraction:
    """Test counting of Quarto callout blocks."""

    def test_counts_callout_blocks(self) -> None:
        qmd = """
::: {.callout-note}
## Key Principle
Content here.
:::

Some text.

::: {.callout-tip}
## Another Note
More content.
:::
"""
        assert count_quarto_callouts(qmd) == 2


class TestAuditExecution:
    """Test end-to-end audit execution on synthetic and live trees."""

    def test_audit_chapter_pair_present_and_absent(self, tmp_path: Path) -> None:
        tex_content = r"""
\chapter{Test Chapter}
\begin{principle}{Core Theorem}{thm:core}
The angular velocity of distal segments increases because inertia decreases.
\end{principle}
\begin{laymansbox}{Missing Box}{box:missing}
This specific explanation about quantum tunneling does not exist in quarto.
\end{laymansbox}
"""
        qmd_content = """
# Test Chapter
::: {.callout-important}
## Core Theorem
The angular velocity of distal segments increases because inertia decreases.
:::
"""
        tex_dir, qmd_dir = create_synthetic_box_tree(
            tmp_path,
            "test_book",
            {"ch01": tex_content},
            {"ch01": qmd_content},
        )
        audit = audit_chapter_boxed_items(
            tex_path=tex_dir / "ch01.tex",
            qmd_path=qmd_dir / "ch01.qmd",
        )
        assert audit.total_boxes == 2
        assert audit.present_boxes == 1
        assert audit.absent_boxes == 1
        assert audit.quarto_callouts_count == 1

    def test_format_markdown_report_structure(self, tmp_path: Path) -> None:
        tex_content = r"\begin{principle}{P1}{p1}Some content with enough words to be substantive\end{principle}"
        qmd_content = (
            "::: {.callout-note}\n## P1\nSome content with enough words to be substantive\n:::"
        )
        tex_dir, qmd_dir = create_synthetic_box_tree(
            tmp_path,
            "test_book",
            {"ch01": tex_content},
            {"ch01": qmd_content},
        )
        book_audit = audit_book_boxed_items(tmp_path / "articles/test_book")
        md = format_markdown_report(book_audit)
        assert "# Boxed Items Parity Audit" in md
        assert "Total LaTeX Boxed Items" in md
        assert "`ch01`" in md

    def test_main_cli_json_and_markdown(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        tex_content = r"\begin{principle}{P1}{p1}Sample body text with enough words to be substantive\end{principle}"
        qmd_content = "Sample body text with enough words to be substantive"
        create_synthetic_box_tree(
            tmp_path,
            "The_Physics_of_Golf",
            {"ch01_test": tex_content},
            {"ch01_test": qmd_content},
        )
        ret = main(["--book", str(tmp_path / "articles/The_Physics_of_Golf"), "--json"])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["book_title"] == "The_Physics_of_Golf"
        assert len(data["chapters"]) == 1
