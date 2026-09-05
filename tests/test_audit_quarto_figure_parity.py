"""Unit and regression tests for scripts/audit_quarto_figure_parity.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_quarto_figure_parity import (
    BookAuditResult,
    ChapterFigureAudit,
    FigureDetail,
    audit_book,
    audit_chapter_pair,
    extract_balanced_latex_arg,
    extract_chapter_title_from_qmd,
    extract_chapter_title_from_tex,
    extract_latex_figures,
    extract_quarto_figures_count,
    extract_quarto_prose_mentions,
    format_markdown_report,
    format_text_summary,
    generate_inventory_doc,
    main,
    strip_latex_comments,
)


def create_synthetic_tree(
    root: Path,
    book_key: str,
    tex_files: dict[str, str],
    qmd_files: dict[str, str],
) -> tuple[Path, Path]:
    """Build a mock directory tree for testing figure parity."""
    tex_dir = root / f"articles/{book_key}/chapters"
    qmd_dir = root / f"articles/{book_key}/quarto"
    tex_dir.mkdir(parents=True, exist_ok=True)
    qmd_dir.mkdir(parents=True, exist_ok=True)

    for stem, content in tex_files.items():
        (tex_dir / f"{stem}.tex").write_text(content, encoding="utf-8")
    for stem, content in qmd_files.items():
        (qmd_dir / f"{stem}.qmd").write_text(content, encoding="utf-8")

    return tex_dir, qmd_dir


class TestTitleExtraction:
    """Test chapter title extraction from TeX and Qmd."""

    def test_extracts_title_from_tex(self) -> None:
        tex = r"\chapter{Dynamics of the Downswing}"
        assert extract_chapter_title_from_tex(tex, "ch01") == "Dynamics of the Downswing"

    def test_extracts_title_from_qmd_yaml_and_heading(self) -> None:
        qmd_yaml = '---\ntitle: "The Kinematic Chain"\n---\nBody'
        assert extract_chapter_title_from_qmd(qmd_yaml, "ch01") == "The Kinematic Chain"

        qmd_heading = "# The Kinematic Chain\nBody"
        assert extract_chapter_title_from_qmd(qmd_heading, "ch01") == "The Kinematic Chain"

        qmd_fallback = "Body without heading"
        assert extract_chapter_title_from_qmd(qmd_fallback, "ch01_test") == "Ch01 Test"


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
        raw = r"\caption{Simple caption}"
        assert extract_balanced_latex_arg(raw, "caption") == "Simple caption"

    def test_extracts_nested_brace_arg(self) -> None:
        raw = r"\caption{Force $\bm{F}_{c}$ at joint \label{fig:joint}}"
        assert (
            extract_balanced_latex_arg(raw, "caption")
            == r"Force $\bm{F}_{c}$ at joint \label{fig:joint}"
        )

    def test_returns_none_when_command_missing(self) -> None:
        raw = r"\othermacro{value}"
        assert extract_balanced_latex_arg(raw, "caption") is None


class TestLatexFigureExtraction:
    """Test LaTeX figure environment parsing."""

    def test_extracts_single_tikz_figure(self) -> None:
        tex = r"""
        \begin{figure}[htbp]
        \centering
        \begin{tikzpicture}
            \draw (0,0) -- (1,1);
        \end{tikzpicture}
        \caption{Arm Model \label{fig:arm_model}}
        \end{figure}
        """
        figs = extract_latex_figures(tex)
        assert len(figs) == 1
        f = figs[0]
        assert f.label == "fig:arm_model"
        assert "Arm Model" in f.caption
        assert f.has_tikzpicture is True
        assert f.has_includegraphics is False
        assert f.tikz_line_count > 0

    def test_extracts_multiple_figures(self) -> None:
        tex = r"""
        \begin{figure}
        \begin{tikzpicture}
            \draw (0,0) circle (1);
        \end{tikzpicture}
        \caption{Fig 1}\label{fig:one}
        \end{figure}
        \begin{figure}
        \includegraphics{pics/diagram.png}
        \caption{Fig 2}\label{fig:two}
        \end{figure}
        """
        figs = extract_latex_figures(tex)
        assert len(figs) == 2
        assert figs[0].label == "fig:one"
        assert figs[0].has_tikzpicture is True
        assert figs[1].label == "fig:two"
        assert figs[1].has_includegraphics is True
        assert figs[1].graphics_target == "pics/diagram.png"

    def test_ignores_commented_out_figures(self) -> None:
        tex = r"""
        % \begin{figure}
        % \begin{tikzpicture}
        % \draw (0,0);
        % \end{tikzpicture}
        % \caption{Ignored}\label{fig:ignored}
        % \end{figure}
        """
        figs = extract_latex_figures(tex)
        assert len(figs) == 0


class TestQuartoFigureExtraction:
    """Test Quarto figure and cross-reference parsing."""

    def test_extracts_markdown_images(self) -> None:
        qmd = "![Diagram](figures/arm.svg){#fig-arm}\nText."
        total, imgs, divs, cells = extract_quarto_figures_count(qmd)
        assert total == 1
        assert imgs == 1
        assert divs == 0
        assert cells == 0

    def test_extracts_quarto_figure_divs(self) -> None:
        qmd = """::: {#fig-landscape}
        ![](figures/landscape.png)
        Caption
        :::"""
        total, imgs, divs, cells = extract_quarto_figures_count(qmd)
        assert total == 2  # 1 div + 1 inner md image = 2 detected constructs
        assert divs == 1
        assert imgs == 1

    def test_extracts_quarto_code_cells_with_figure_label(self) -> None:
        qmd = """```{python}
#| label: fig-trajectory
#| fig-cap: "Trajectory plot"
import matplotlib.pyplot as plt
```"""
        total, imgs, divs, cells = extract_quarto_figures_count(qmd)
        assert total == 1
        assert cells == 1

    def test_extracts_prose_figure_mentions(self) -> None:
        qmd = """
        # Chapter 1
        <!-- Note: TikZ figure replaced with description. -->
        As seen in Figure 1, the arm accelerates.
        In Fig. 2 we observe a phase transition.
        """
        mentions = extract_quarto_prose_mentions(qmd)
        assert len(mentions) == 2
        assert "Figure 1" in mentions[0]
        assert "Fig. 2" in mentions[1]


class TestAuditChapterPair:
    """Test chapter-level audit comparison."""

    def test_detects_missing_figures_in_quarto(self, tmp_path: Path) -> None:
        tex_file = tmp_path / "ch01_test.tex"
        qmd_file = tmp_path / "ch01_test.qmd"

        tex_file.write_text(
            r"""\chapter{Test Chapter}
            \begin{figure}
            \begin{tikzpicture}
            \draw (0,0);
            \end{tikzpicture}
            \caption{Test Figure}\label{fig:test}
            \end{figure}
            """,
            encoding="utf-8",
        )
        qmd_file.write_text("# Test Chapter\nNo figures here.\n", encoding="utf-8")

        audit = audit_chapter_pair(tex_file, qmd_file, "ch01_test", tmp_path)
        assert audit.latex_figure_count == 1
        assert audit.quarto_figure_count == 0
        assert audit.parity_delta == -1
        assert audit.is_in_parity is False
        assert audit.chapter_title == "Test Chapter"

    def test_detects_parity_when_figures_match(self, tmp_path: Path) -> None:
        tex_file = tmp_path / "ch01_test.tex"
        qmd_file = tmp_path / "ch01_test.qmd"

        tex_file.write_text(
            r"""\chapter{Test Chapter}
            \begin{figure}
            \begin{tikzpicture}
            \draw (0,0);
            \end{tikzpicture}
            \caption{Test Figure}\label{fig:test}
            \end{figure}
            """,
            encoding="utf-8",
        )
        qmd_file.write_text(
            "# Test Chapter\n![Test Figure](fig.svg){#fig-test}\n",
            encoding="utf-8",
        )

        audit = audit_chapter_pair(tex_file, qmd_file, "ch01_test", tmp_path)
        assert audit.latex_figure_count == 1
        assert audit.quarto_figure_count == 1
        assert audit.parity_delta == 0
        assert audit.is_in_parity is True

    def test_handles_missing_quarto_file(self, tmp_path: Path) -> None:
        tex_file = tmp_path / "ch32_putting.tex"
        tex_file.write_text(r"\chapter{Putting}\n", encoding="utf-8")

        audit = audit_chapter_pair(tex_file, None, "ch32_putting", tmp_path)
        assert audit.latex_figure_count == 0
        assert audit.quarto_figure_count == 0
        assert audit.qmd_path is None
        assert audit.is_in_parity is True


class TestAuditBookPhysicsOfGolf:
    """Integration test auditing the actual repository Physics of Golf tree."""

    def test_audits_physics_of_golf_repository_tree(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        res = audit_book(repo_root, "The_Physics_of_Golf")

        assert res.book_name == "The_Physics_of_Golf"
        assert res.total_chapters == 34
        # #4149 removes two unsupported physiological diagrams from chapter 9b.
        assert res.chapters_with_latex_figures == 28
        assert res.total_latex_figures == 29
        # #4160, #4161, and #4164 replace diagrams with shared print/web images.
        assert res.total_latex_tikz == 26
        assert res.total_latex_includegraphics == 3
        assert res.total_latex_fig_labels == 29
        assert res.total_quarto_figures == 3
        assert res.missing_figures_count == 26
        assert res.is_in_full_parity is False


class TestFormattingAndReporting:
    """Test text, markdown, and doc generation."""

    def test_format_text_summary(self) -> None:
        detail = FigureDetail(1, "fig:a", "Cap", True, False, None, 5)
        ch = ChapterFigureAudit(
            "ch01",
            "Ch1",
            "ch01.tex",
            "ch01.qmd",
            1,
            1,
            0,
            ["fig:a"],
            [],
            0,
            0,
            0,
            0,
            [],
            [],
            [],
            [detail],
        )
        res = BookAuditResult("TestBook", 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, [ch])
        summary = format_text_summary(res)
        assert "=== Figure Parity Audit: TestBook ===" in summary
        assert "Total Chapters Audited: 1" in summary
        assert "Parity Gap (Missing Figures): 1" in summary

    def test_format_markdown_report(self) -> None:
        detail = FigureDetail(1, "fig:a", "Cap", True, False, None, 5)
        ch = ChapterFigureAudit(
            "ch01",
            "Ch1",
            "ch01.tex",
            "ch01.qmd",
            1,
            1,
            0,
            ["fig:a"],
            [],
            0,
            0,
            0,
            0,
            [],
            [],
            [],
            [detail],
        )
        res = BookAuditResult("TestBook", 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, [ch])
        md = format_markdown_report(res)
        assert "# Figures Inventory and Parity Audit: TestBook" in md
        assert "| **Total LaTeX Figures** | 1 |" in md
        assert "| `ch01` | 1 | `fig:a` | TikZ Diagram | Cap |" in md

    def test_generate_inventory_doc(self, tmp_path: Path) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        out_file = tmp_path / "INVENTORY_TEST.md"
        doc = generate_inventory_doc(repo_root, out_file)
        assert doc.exists()
        content = doc.read_text(encoding="utf-8")
        assert "# Figures Inventory and Parity Audit: The Physics of Golf" in content
        assert "31" in content


class TestCLI:
    """Test CLI execution modes."""

    def test_cli_json_mode(self, capsys: pytest.CaptureFixture[str]) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        ret = main(["--json", "--repo-root", str(repo_root)])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["book_name"] == "The_Physics_of_Golf"
        assert data["total_chapters"] == 34
        assert data["total_latex_figures"] == 29

    def test_cli_check_mode_fails_when_discrepancy(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        ret = main(["--check", "--repo-root", str(repo_root)])
        assert ret == 1

    def test_cli_invalid_book_fails(self) -> None:
        with pytest.raises(SystemExit):
            main(["--book", "Invalid_Book"])
