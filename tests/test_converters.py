"""Tests for converter tool modules: conversion_batch and latex_to_quarto."""

from __future__ import annotations

import logging
import tempfile
from unittest.mock import MagicMock

from src.tools.conversion_batch import FileConverter, run_batch_conversion
from src.tools.latex_to_quarto import _build_yaml_frontmatter, latex_to_quarto_md

# ---------------------------------------------------------------------------
# conversion_batch module tests
# ---------------------------------------------------------------------------


class TestRunBatchConversion:
    """Tests for run_batch_conversion helper."""

    def _make_logger(self) -> logging.Logger:
        return logging.getLogger("test_converters")

    def _make_converter(self) -> MagicMock:
        converter = MagicMock(spec=FileConverter)
        return converter

    def test_import_run_batch_conversion(self) -> None:
        """run_batch_conversion is importable from conversion_batch."""
        assert callable(run_batch_conversion)

    def test_import_file_converter_protocol(self) -> None:
        """FileConverter protocol is importable from conversion_batch."""
        assert callable(getattr(FileConverter, "convert_file", None) or FileConverter)

    def test_empty_conversions_returns_zero_counts(self) -> None:
        """Empty conversion list returns (0, 0)."""
        logger = self._make_logger()
        converter = self._make_converter()
        success, errors = run_batch_conversion(
            conversions=[],
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 0
        assert errors == 0

    def test_dry_run_counts_success_without_calling_converter(self) -> None:
        """In dry_run mode, existing files are counted as success without conversion."""
        logger = self._make_logger()
        converter = self._make_converter()

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        conversions = [{"source": tmp_path, "target": "/tmp/out.qmd"}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=True,
        )
        assert success == 1
        assert errors == 0
        converter.convert_file.assert_not_called()

    def test_missing_source_file_increments_error_count(self) -> None:
        """Non-existent source file increments error count."""
        logger = self._make_logger()
        converter = self._make_converter()
        conversions = [{"source": "/nonexistent/path.tex", "target": "/tmp/out.qmd"}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 0
        assert errors == 1

    def test_invalid_entry_missing_source_key_increments_error(self) -> None:
        """Conversion entry without 'source' key increments error count."""
        logger = self._make_logger()
        converter = self._make_converter()
        conversions = [{"target": "/tmp/out.qmd"}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 0
        assert errors == 1

    def test_invalid_entry_missing_target_key_increments_error(self) -> None:
        """Conversion entry without 'target' key increments error count."""
        logger = self._make_logger()
        converter = self._make_converter()
        conversions = [{"source": "/tmp/some.tex"}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 0
        assert errors == 1

    def test_converter_exception_increments_error_count(self) -> None:
        """When converter.convert_file raises OSError, error count increments."""
        logger = self._make_logger()
        converter = self._make_converter()
        converter.convert_file.side_effect = OSError("disk full")

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        conversions = [{"source": tmp_path, "target": "/tmp/out.qmd"}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 0
        assert errors == 1

    def test_successful_conversion_calls_convert_file(self) -> None:
        """Successful conversion calls converter.convert_file with correct args."""
        logger = self._make_logger()
        converter = self._make_converter()

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        target = "/tmp/output.qmd"
        conversions = [{"source": tmp_path, "target": target}]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 1
        assert errors == 0
        converter.convert_file.assert_called_once_with(tmp_path, target)

    def test_description_key_used_when_source_missing(self) -> None:
        """description_key is used in warning log when source is missing."""
        logger = self._make_logger()
        converter = self._make_converter()
        conversions = [{"source": "/no/such/file.tex", "target": "/tmp/out.qmd", "name": "my doc"}]
        _, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
            description_key="name",
        )
        assert errors == 1

    def test_multiple_conversions_mixed_results(self) -> None:
        """Mixed valid/invalid conversions produce correct success and error counts."""
        logger = self._make_logger()
        converter = self._make_converter()

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        conversions = [
            {"source": tmp_path, "target": "/tmp/out1.qmd"},
            {"source": "/nonexistent.tex", "target": "/tmp/out2.qmd"},
        ]
        success, errors = run_batch_conversion(
            conversions=conversions,
            converter=converter,
            logger=logger,
            dry_run=False,
        )
        assert success == 1
        assert errors == 1


# ---------------------------------------------------------------------------
# latex_to_quarto module tests
# ---------------------------------------------------------------------------


class TestBuildYamlFrontmatter:
    """Tests for _build_yaml_frontmatter helper."""

    def test_basic_title_included(self) -> None:
        """Title appears in frontmatter output."""
        result = _build_yaml_frontmatter("My Title", toc=False, abstract=None)
        assert "My Title" in result

    def test_toc_true_includes_toc_directive(self) -> None:
        """toc: True adds toc directive to frontmatter."""
        result = _build_yaml_frontmatter("T", toc=True, abstract=None)
        assert "toc: true" in result

    def test_toc_false_omits_toc_directive(self) -> None:
        """toc: False omits toc directive from frontmatter."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert "toc: true" not in result

    def test_abstract_included_when_provided(self) -> None:
        """Abstract text appears in frontmatter when provided."""
        result = _build_yaml_frontmatter("T", toc=False, abstract="This is the abstract.")
        assert "This is the abstract." in result

    def test_no_abstract_when_none(self) -> None:
        """No abstract block when abstract is None."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert "abstract" not in result

    def test_output_starts_with_yaml_delimiter(self) -> None:
        """Frontmatter starts with YAML delimiter '---'."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert result.startswith("---")

    def test_output_ends_with_double_newline(self) -> None:
        """Frontmatter ends with two newlines after closing delimiter."""
        result = _build_yaml_frontmatter("T", toc=False, abstract=None)
        assert result.endswith("\n\n")


class TestLatexToQuartoMd:
    """Tests for the latex_to_quarto_md conversion function."""

    def test_basic_conversion_returns_tuple(self) -> None:
        """latex_to_quarto_md returns a 3-tuple (md, before_wc, after_wc)."""
        tex = r"\begin{document}Hello world.\end{document}"
        result = latex_to_quarto_md(tex, "fallback")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_body_content_preserved(self) -> None:
        """Body text from LaTeX appears in the converted Quarto markdown."""
        tex = r"\begin{document}Important content here.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "Important content here." in md

    def test_section_converted_to_heading(self) -> None:
        r"""LaTeX \section is converted to Markdown # heading."""
        tex = r"\begin{document}\section{Introduction}Text.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "fallback")
        assert "# Introduction" in md

    def test_fallback_title_used_when_no_title_command(self) -> None:
        """Fallback title is used when LaTeX has no \\title command."""
        tex = r"\begin{document}Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "My Fallback Title")
        assert "My Fallback Title" in md

    def test_title_command_takes_priority_over_fallback(self) -> None:
        r"""Explicit \title command takes priority over fallback."""
        tex = r"\title{Explicit Title}\begin{document}Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "Fallback")
        assert "Explicit Title" in md

    def test_word_counts_are_positive_integers(self) -> None:
        """Word count values returned are non-negative integers."""
        tex = r"\begin{document}Some text here.\end{document}"
        _, before_wc, after_wc = latex_to_quarto_md(tex, "title")
        assert isinstance(before_wc, int)
        assert isinstance(after_wc, int)
        assert before_wc >= 0
        assert after_wc >= 0

    def test_minimal_document_body_handled(self) -> None:
        """Minimal document body with whitespace content does not raise an exception."""
        tex = r"\begin{document} \end{document}"
        md, _, _ = latex_to_quarto_md(tex, "empty")
        assert isinstance(md, str)

    def test_toc_detected_and_removed_from_body(self) -> None:
        r"""\\tableofcontents is removed from body and triggers toc: true in frontmatter."""
        tex = r"\begin{document}\tableofcontents Content.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "\\tableofcontents" not in md
        assert "toc: true" in md

    def test_abstract_extracted_into_frontmatter(self) -> None:
        """Abstract block is extracted and placed in YAML frontmatter."""
        tex = (
            r"\begin{document}"
            r"\begin{abstract}This is the abstract.\end{abstract}"
            r"Body text.\end{document}"
        )
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "This is the abstract." in md
        assert "\\begin{abstract}" not in md

    def test_subsection_converted_to_heading(self) -> None:
        r"""LaTeX \subsection is converted to Markdown ## heading."""
        tex = r"\begin{document}\subsection{Background}Text.\end{document}"
        md, _, _ = latex_to_quarto_md(tex, "title")
        assert "## Background" in md
