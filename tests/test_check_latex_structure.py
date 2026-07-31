"""Tests for the LaTeX structural pre-check.

Each rule gets a fixture that reproduces a defect the 2026-07-31 content review
actually found in this repository, plus a negative case proving the rule does not
fire on legitimate LaTeX. The negative cases matter as much as the positive ones:
an early draft of this checker flagged every ordinary trailing comment as an
unescaped percent sign, which would have made it useless as a gate.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_latex_structure import (
    SourceFile,
    check_citations,
    check_document_environments,
    check_environment_balance,
    check_markdown_fences,
    check_master_has_end_document,
    check_section_braces,
    check_truncation,
    check_unescaped_percent,
    collect_bib_keys,
    main,
    run,
)


def write(tmp_path: Path, name: str, body: str) -> SourceFile:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return SourceFile.load(path)


def rules(findings) -> set[str]:
    return {finding.rule for finding in findings}


class TestStrayDocumentEnvironment:
    def test_flags_end_document_in_chapter(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch03.tex", "Text.\n\\end{document}\n")
        findings = check_document_environments(source)
        assert rules(findings) == {"stray-document"}
        assert findings[0].line == 2

    def test_master_file_may_close_the_document(self, tmp_path: Path) -> None:
        source = write(
            tmp_path, "main.tex", "\\documentclass{book}\n\\begin{document}\nHi.\n\\end{document}\n"
        )
        assert check_document_environments(source) == []


class TestEnvironmentBalance:
    def test_flags_unclosed_environment(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "\\begin{itemize}\n\\item One.\n")
        findings = check_environment_balance(source)
        assert [finding.rule for finding in findings] == ["unbalanced-environment"]
        assert "itemize" in findings[0].message

    def test_ignores_environment_named_inside_a_comment(self, tmp_path: Path) -> None:
        """Regression: Volume_0/main.tex mentions \\begin{algorithmic} in a comment.

        Counting without stripping comments reports that file as unbalanced.
        """
        body = (
            "% Backward-compat alias so existing \\begin{algorithmic} still compiles:\n"
            "\\newenvironment{algorithmic}{}{}\n"
        )
        source = write(tmp_path, "main.tex", body)
        assert check_environment_balance(source) == []

    def test_ignores_markup_inside_verbatim(self, tmp_path: Path) -> None:
        body = "\\begin{lstlisting}\n\\begin{itemize}\n\\end{lstlisting}\n"
        source = write(tmp_path, "ch.tex", body)
        assert check_environment_balance(source) == []

    def test_balanced_file_is_clean(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "\\begin{itemize}\n\\item One.\n\\end{itemize}\n")
        assert check_environment_balance(source) == []


class TestTruncation:
    def test_flags_file_ending_mid_sentence(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch30.tex", "Some prose.\n\\item[(c)] For a system excited by")
        findings = check_truncation(source)
        assert rules(findings) == {"truncated-file"}

    @pytest.mark.parametrize(
        "ending",
        ["End of sentence.", "\\end{itemize}", "\\cleardoublepage", "\\newpage", "% a comment"],
    )
    def test_accepts_legitimate_endings(self, tmp_path: Path, ending: str) -> None:
        source = write(tmp_path, "ch.tex", f"Body text.\n{ending}\n")
        assert check_truncation(source) == []


class TestMasterEndDocument:
    def test_flags_master_without_end_document(self, tmp_path: Path) -> None:
        source = write(tmp_path, "main.tex", "\\documentclass{book}\n\\begin{document}\nHi.\n")
        assert rules(check_master_has_end_document(source)) == {"missing-end-document"}

    def test_chapter_is_not_required_to_close_the_document(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "Just prose.\n")
        assert check_master_has_end_document(source) == []


class TestSectionBraces:
    def test_flags_unclosed_section_argument(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch16.tex", "\\subsection{Connection to Control**\n\nBody.\n")
        assert rules(check_section_braces(source)) == {"unclosed-section-brace"}

    def test_allows_title_wrapping_across_lines(self, tmp_path: Path) -> None:
        """Regression: a section title may legitimately span source lines."""
        body = "\\subsection{The Essence of\n  Contraction}\n\nBody.\n"
        source = write(tmp_path, "ch.tex", body)
        assert check_section_braces(source) == []

    def test_allows_nested_braces_in_title(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "\\section{A \\textbf{bold} title}\n")
        assert check_section_braces(source) == []


class TestMarkdownFences:
    def test_flags_markdown_fence(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch23.tex", "Text.\n```xml\n<robot/>\n```\n")
        assert rules(check_markdown_fences(source)) == {"markdown-fence"}

    def test_lstlisting_is_fine(self, tmp_path: Path) -> None:
        body = "\\begin{lstlisting}[language=XML]\n<robot/>\n\\end{lstlisting}\n"
        source = write(tmp_path, "ch.tex", body)
        assert check_markdown_fences(source) == []


class TestUnescapedPercent:
    def test_flags_percent_sign_after_a_digit(self, tmp_path: Path) -> None:
        body = "Segment masses are measured with ~5-10% error. How sensitive is the model?\n"
        source = write(tmp_path, "ch23.tex", body)
        assert rules(check_unescaped_percent(source)) == {"unescaped-percent"}

    def test_escaped_percent_is_fine(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "Measured with ~5-10\\% error. Fine.\n")
        assert check_unescaped_percent(source) == []

    def test_ordinary_trailing_comment_is_not_flagged(self, tmp_path: Path) -> None:
        """Regression: an early draft flagged every commented preamble line."""
        source = write(tmp_path, "ch.tex", "\\usepackage{textcomp} % provide euro symbol\n")
        assert check_unescaped_percent(source) == []

    def test_line_continuation_idiom_is_not_flagged(self, tmp_path: Path) -> None:
        """``\\epigraph{%`` suppresses a newline and is used in five chapters."""
        source = write(tmp_path, "ch.tex", "\\epigraph{%\n  A quotation.\n}{Author}\n")
        assert check_unescaped_percent(source) == []


class TestCitations:
    def test_flags_prose_written_into_cite(self, tmp_path: Path) -> None:
        body = "Claim \\cite{published measurement or CFD estimate for energy loss}.\n"
        source = write(tmp_path, "ch19.tex", body)
        assert rules(check_citations(source, {"Real2020"})) == {"prose-in-cite"}

    def test_flags_key_with_no_bibliography_entry(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "Claim \\cite{Todorov2002}.\n")
        assert rules(check_citations(source, {"Real2020"})) == {"unresolved-citation"}

    def test_resolving_key_is_clean(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "Claim \\cite{Real2020}.\n")
        assert check_citations(source, {"Real2020"}) == []

    def test_non_ascii_key_is_not_prose(self, tmp_path: Path) -> None:
        """Regression: 'Schoner2003' spelled with an umlaut is a key, not prose."""
        source = write(tmp_path, "ch.tex", "Claim \\cite{Sch\u00f6ner2003}.\n")
        assert rules(check_citations(source, {"Sch\u00f6ner2003"})) == set()

    def test_multiple_keys_checked_separately(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "Claim \\cite{Good2020,Missing2021}.\n")
        findings = check_citations(source, {"Good2020"})
        assert len(findings) == 1
        assert "Missing2021" in findings[0].message

    def test_citation_inside_a_comment_is_ignored(self, tmp_path: Path) -> None:
        # The fixture text avoids the usual task-marker keywords: the repo-wide
        # code-quality gate flags those anywhere they are not tied to a tracked
        # issue, and it does not exempt test fixtures.
        source = write(tmp_path, "ch.tex", "% draft note \\cite{NotRealYet}\n")
        assert check_citations(source, {"Real2020"}) == []

    def test_citeneeded_marker_is_not_a_citation(self, tmp_path: Path) -> None:
        """Regression: `\\citeneeded` is a deliberate marker, not a broken citation.

        `golf_physics.sty` defines it to render a visible red
        "[citation needed: <description>]" superscript. Its argument is prose by
        design. An earlier draft matched any command containing "cite" and
        flagged all eight uses as malformed citations -- penalising the project
        for being honest about what it has not sourced yet.
        """
        body = "Grip force is 40--60 N.\\citeneeded{measured grip force during golf swing}\n"
        source = write(tmp_path, "ch04.tex", body)
        assert check_citations(source, {"Real2020"}) == []

    def test_nocite_is_not_checked(self, tmp_path: Path) -> None:
        source = write(tmp_path, "ch.tex", "\\nocite{*}\n")
        assert check_citations(source, {"Real2020"}) == []

    def test_real_citations_are_still_checked_alongside_markers(self, tmp_path: Path) -> None:
        """Excluding the marker must not blind the rule to genuine citations."""
        body = "Claim \\citeneeded{a source we still want} and \\cite{Missing2021}.\n"
        source = write(tmp_path, "ch.tex", body)
        findings = check_citations(source, {"Real2020"})
        assert rules(findings) == {"unresolved-citation"}
        assert "Missing2021" in findings[0].message


class TestBibliographyParsing:
    def test_collects_keys(self, tmp_path: Path) -> None:
        bib = tmp_path / "refs.bib"
        bib.write_text(
            "@article{Todorov2002,\n  title = {Optimal feedback control},\n}\n"
            "@book{ Featherstone2008 ,\n  title = {Rigid Body Dynamics Algorithms},\n}\n",
            encoding="utf-8",
        )
        assert collect_bib_keys([bib]) == {"Todorov2002", "Featherstone2008"}

    def test_missing_file_is_tolerated(self, tmp_path: Path) -> None:
        assert collect_bib_keys([tmp_path / "absent.bib"]) == set()


class TestRun:
    def test_clean_tree_produces_no_findings(self, tmp_path: Path) -> None:
        (tmp_path / "refs.bib").write_text("@book{Key2020,\n title={T},\n}\n", encoding="utf-8")
        (tmp_path / "ch.tex").write_text(
            "\\begin{itemize}\n\\item Cited \\cite{Key2020}.\n\\end{itemize}\n", encoding="utf-8"
        )
        assert run(tmp_path) == []

    def test_exclusions_are_honoured(self, tmp_path: Path) -> None:
        drafts = tmp_path / "drafts"
        drafts.mkdir()
        (drafts / "broken.tex").write_text("\\begin{itemize}\n", encoding="utf-8")
        assert run(tmp_path) != []
        assert run(tmp_path, exclude=("drafts",)) == []


class TestBaselineRatchet:
    """The gate must accept known defects while refusing to let new ones land."""

    def _corpus(self, tmp_path: Path) -> Path:
        (tmp_path / "known.tex").write_text("\\begin{itemize}\n\\item One.\n", encoding="utf-8")
        return tmp_path

    def test_known_findings_pass_once_baselined(self, tmp_path: Path) -> None:
        root = self._corpus(tmp_path)
        baseline = tmp_path / "baseline.json"
        assert main(["--root", str(root), "--baseline", str(baseline), "--write-baseline"]) == 0
        assert main(["--root", str(root), "--baseline", str(baseline)]) == 0

    def test_new_finding_fails_even_with_a_baseline(self, tmp_path: Path) -> None:
        root = self._corpus(tmp_path)
        baseline = tmp_path / "baseline.json"
        main(["--root", str(root), "--baseline", str(baseline), "--write-baseline"])
        (root / "fresh.tex").write_text("Body.\n\\end{document}\n", encoding="utf-8")
        assert main(["--root", str(root), "--baseline", str(baseline)]) == 1

    def test_without_a_baseline_any_finding_fails(self, tmp_path: Path) -> None:
        assert main(["--root", str(self._corpus(tmp_path))]) == 1

    def test_fingerprint_survives_line_shifts(self, tmp_path: Path) -> None:
        """Fixing an earlier defect must not resurface later ones as 'new'."""
        root = tmp_path
        (root / "ch.tex").write_text("Line one.\n\\begin{itemize}\n\\item A.\n", encoding="utf-8")
        baseline = tmp_path / "baseline.json"
        main(["--root", str(root), "--baseline", str(baseline), "--write-baseline"])
        # Insert prose above the defect, shifting its line number.
        (root / "ch.tex").write_text(
            "Line one.\nInserted paragraph.\n\\begin{itemize}\n\\item A.\n", encoding="utf-8"
        )
        assert main(["--root", str(root), "--baseline", str(baseline)]) == 0

    def test_write_baseline_requires_a_path(self, tmp_path: Path) -> None:
        assert main(["--root", str(self._corpus(tmp_path)), "--write-baseline"]) == 2
