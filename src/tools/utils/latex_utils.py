"""Shared LaTeX parsing utilities for DRY consolidation.

This module extracts common LaTeX-related operations used across the
three converter scripts (latex_to_html, latex_to_qmd, latex_to_quarto),
eliminating the DRY violation identified in the code quality assessment.

Shared operations:
- Title/author/abstract extraction
- Section command → heading conversion
- List environment conversion (itemize, enumerate)
- LaTeX comment removal
- Common command cleanup (labels, vspace, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.core.contracts import require
from src.tools.utils import setup_logging

logger = setup_logging(__name__)


# ─── Data Structures ────────────────────────────────────────────


@dataclass
class LaTeXMetadata:
    """Parsed metadata from a LaTeX document."""

    title: str = "Untitled"
    author: str = ""
    date: str = ""
    abstract: str = ""
    has_toc: bool = False
    extra: dict[str, str] = field(default_factory=dict)


# ─── Metadata Extraction ────────────────────────────────────────


def extract_title(latex_content: str, fallback: str = "Untitled Article") -> str:
    r"""Extract \title{...} from LaTeX content.

    Args:
        latex_content: Raw LaTeX source text.
        fallback: Default title if none found.

    Returns:
        Extracted title string, cleaned of formatting commands.
    """
    m = re.search(r"\\title\{((?:[^{}]|\{[^{}]*\})*)\}", latex_content, re.DOTALL)
    if not m:
        return fallback

    title = m.group(1).strip()
    # Remove formatting: \textbf{...}, \\, etc.
    title = re.sub(r"\\textbf\{([^}]+)\}", r"\1", title)
    title = re.sub(r"\\\\\[[^\]]+\]", " ", title)
    title = re.sub(r"\\\\", " ", title)
    return title.strip()


def extract_author(latex_content: str) -> str:
    r"""Extract \author{...} from LaTeX content."""
    m = re.search(r"\\author\{([^}]*)\}", latex_content, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_abstract(latex_content: str) -> str:
    r"""Extract \begin{abstract}...\end{abstract} from LaTeX content."""
    m = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        latex_content,
        re.DOTALL,
    )
    return m.group(1).strip() if m else ""


def extract_body(latex_content: str) -> str:
    r"""Extract content between \begin{document} and \end{document}."""
    m_begin = re.search(r"\\begin\{document\}", latex_content)
    m_end = re.search(r"\\end\{document\}", latex_content)
    start = m_begin.end() if m_begin else 0
    end = m_end.start() if m_end else len(latex_content)
    return latex_content[start:end]


def extract_metadata(latex_content: str, fallback_title: str = "Untitled") -> LaTeXMetadata:
    """Extract all standard metadata from LaTeX content.

    Args:
        latex_content: Raw LaTeX source text.
        fallback_title: Default title if \\title{} not found.

    Returns:
        Populated LaTeXMetadata instance.
    """
    require(len(latex_content) > 0, "latex_content must not be empty")
    return LaTeXMetadata(
        title=extract_title(latex_content, fallback_title),
        author=extract_author(latex_content),
        abstract=extract_abstract(latex_content),
        has_toc=bool(re.search(r"\\tableofcontents", latex_content)),
    )


# ─── Section Conversion ─────────────────────────────────────────


def convert_sections_to_markdown(content: str) -> str:
    r"""Convert \section, \subsection, \subsubsection to markdown headings."""
    content = re.sub(r"\\section\*?\{([^}]*)\}", r"\n\n# \1\n\n", content)
    content = re.sub(r"\\subsection\*?\{([^}]*)\}", r"\n\n## \1\n\n", content)
    content = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"\n\n### \1\n\n", content)
    return content


def convert_sections_to_html(content: str) -> str:
    r"""Convert \section, \subsection, \subsubsection to HTML headings."""
    content = re.sub(r"\\section\{([^}]+)\}", r"<h2>\1</h2>", content)
    content = re.sub(r"\\subsection\{([^}]+)\}", r"<h3>\1</h3>", content)
    content = re.sub(r"\\subsubsection\{([^}]+)\}", r"<h4>\1</h4>", content)
    return content


# ─── Text Formatting ────────────────────────────────────────────


def convert_text_formatting_to_markdown(content: str) -> str:
    r"""Convert \textbf, \textit, \emph, \texttt to markdown equivalents."""
    content = re.sub(r"\\textbf\{([^}]+)\}", r"**\1**", content)
    content = re.sub(r"\\textit\{([^}]+)\}", r"*\1*", content)
    content = re.sub(r"\\emph\{([^}]+)\}", r"*\1*", content)
    content = re.sub(r"\\texttt\{([^}]+)\}", r"`\1`", content)
    return content


def convert_text_formatting_to_html(content: str) -> str:
    r"""Convert \textbf, \textit, \emph, \texttt to HTML elements."""
    content = re.sub(r"\\textbf\{([^}]+)\}", r"<strong>\1</strong>", content)
    content = re.sub(r"\\textit\{([^}]+)\}", r"<em>\1</em>", content)
    content = re.sub(r"\\emph\{([^}]+)\}", r"<em>\1</em>", content)
    content = re.sub(r"\\texttt\{([^}]+)\}", r"<code>\1</code>", content)
    return content


# ─── List Conversion ─────────────────────────────────────────────


def _itemize_to_markdown(match: re.Match[str]) -> str:
    """Convert an itemize block to markdown unordered list."""
    items = match.group(1)
    items = re.sub(r"\\item\s+", "- ", items)
    items = re.sub(r"\\item\s*$", "- ", items, flags=re.MULTILINE)
    return items


def _enumerate_to_markdown(match: re.Match[str]) -> str:
    """Convert an enumerate block to markdown ordered list."""
    items = match.group(1)
    counter = [0]

    def number_item(m: re.Match[str]) -> str:
        """Increment counter and return numbered list prefix."""
        counter[0] += 1
        return f"{counter[0]}. "

    items = re.sub(r"\\item\s+", number_item, items)
    items = re.sub(r"\\item\s*$", number_item, items, flags=re.MULTILINE)
    return items


def convert_lists_to_markdown(content: str) -> str:
    """Convert LaTeX itemize/enumerate to markdown lists."""
    content = re.sub(
        r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
        _itemize_to_markdown,
        content,
        flags=re.DOTALL,
    )
    return re.sub(
        r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}",
        _enumerate_to_markdown,
        content,
        flags=re.DOTALL,
    )


def _itemize_to_html(match: re.Match[str]) -> str:
    """Convert an itemize block to HTML unordered list."""
    items = match.group(1)
    items = re.sub(r"\\item\s+", "<li>", items)
    items = re.sub(r"\\item\s*$", "<li>", items, flags=re.MULTILINE)
    items = re.sub(r"(<li>.*?)(?=<li>|$)", r"\1</li>", items, flags=re.DOTALL)
    return f"<ul>\n{items}\n</ul>"


def _enumerate_to_html(match: re.Match[str]) -> str:
    """Convert an enumerate block to HTML ordered list."""
    items = match.group(1)
    items = re.sub(r"\\item\s+", "<li>", items)
    items = re.sub(r"\\item\s*$", "<li>", items, flags=re.MULTILINE)
    items = re.sub(r"(<li>.*?)(?=<li>|$)", r"\1</li>", items, flags=re.DOTALL)
    return f"<ol>\n{items}\n</ol>"


def convert_lists_to_html(content: str) -> str:
    """Convert LaTeX itemize/enumerate to HTML lists."""
    content = re.sub(
        r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
        _itemize_to_html,
        content,
        flags=re.DOTALL,
    )
    return re.sub(
        r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}",
        _enumerate_to_html,
        content,
        flags=re.DOTALL,
    )


# ─── Common Cleanup ─────────────────────────────────────────────


def remove_comments(content: str) -> str:
    """Remove LaTeX comments (lines starting with % and inline comments)."""
    content = re.sub(r"^%.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"%.*", "", content)
    return content


def remove_document_structure(content: str) -> str:
    r"""Remove \maketitle, \title{}, \author{}, \date{}, etc."""
    content = re.sub(r"\\maketitle", "", content)
    content = re.sub(r"\\title\{[^}]*\}", "", content)
    content = re.sub(r"\\author\{[^}]*\}", "", content)
    content = re.sub(r"\\date\{[^}]*\}", "", content)
    return content


def remove_labels(content: str) -> str:
    r"""Remove all \label{...} commands."""
    return re.sub(r"\\label\{[^}]+\}", "", content)


def remove_spacing_commands(content: str) -> str:
    r"""Remove \vspace, \hspace and font size commands."""
    content = re.sub(r"\\[vh]space\*?\{[^}]+\}", "", content)
    content = re.sub(
        r"\\(small|large|Large|huge|Huge|tiny|footnotesize|scriptsize|normalsize)",
        "",
        content,
    )
    return content


def clean_common_latex(content: str) -> str:
    """Apply all common cleanup operations in one pass.

    Removes comments, labels, spacing commands, and structural commands.
    This is the single-call entry point for shared cleanup.
    """
    require(len(content) > 0, "content must not be empty for cleanup")
    content = remove_comments(content)
    content = remove_document_structure(content)
    content = remove_labels(content)
    content = remove_spacing_commands(content)
    return content


# ─── URL / Reference Conversion ─────────────────────────────────


def convert_urls_to_markdown(content: str) -> str:
    r"""Convert \url{} and \href{}{} to markdown links."""
    content = re.sub(r"\\url\{([^}]+)\}", r"[\1](\1)", content)
    content = re.sub(r"\\href\{([^}]+)\}\{([^}]+)\}", r"[\2](\1)", content)
    return content


def convert_urls_to_html(content: str) -> str:
    r"""Convert \url{} and \href{}{} to HTML links."""
    content = re.sub(
        r"\\url\{([^}]+)\}",
        r'<a href="\1" target="_blank">\1</a>',
        content,
    )
    content = re.sub(
        r"\\href\{([^}]+)\}\{([^}]+)\}",
        r'<a href="\1" target="_blank">\2</a>',
        content,
    )
    return content


def convert_references(content: str) -> str:
    r"""Convert \ref{} and \cref{} to plain text."""
    content = re.sub(r"\\cref\{([^}]+)\}", r"Figure \1", content)
    content = re.sub(r"\\ref\{([^}]+)\}", r"\1", content)
    return content


def convert_quotes(content: str) -> str:
    """Convert LaTeX-style quotes (`` and '') to standard quotes."""
    content = re.sub(r"``", '"', content)
    content = re.sub(r"''", '"', content)
    return content
