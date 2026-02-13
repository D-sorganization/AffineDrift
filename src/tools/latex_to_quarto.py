"""Convert LaTeX documents to Quarto markdown format.

This tool converts individual LaTeX (.tex) files to Quarto markdown (.qmd)
format, preserving mathematical equations, document structure, and formatting.

Usage:
    python latex_to_quarto.py <input.tex> [output.qmd]

Example:
    python latex_to_quarto.py article.tex
    python latex_to_quarto.py article.tex articles/article.qmd

Features:
- Preserves LaTeX math environments
- Converts document structure to Quarto equivalents
- Handles bibliographic references
- Generates appropriate YAML frontmatter
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.tools.utils import find_files_by_extension, setup_logging
from src.tools.utils.latex_utils import (
    clean_common_latex,
    convert_sections_to_markdown,
    extract_body,
    extract_title,
)

logger = setup_logging(__name__)


def prompt_for_files() -> list[Path]:
    """Fallback to GUI if no command-line arguments provided."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(
            title="Select LaTeX files to convert",
            filetypes=[("LaTeX files", "*.tex"), ("All files", "*.*")],
        )
        return [Path(f) for f in file_paths]
    except ImportError:
        sys.exit(1)


def latex_to_quarto_md(tex_text: str, fallback_title: str) -> tuple[str, int, int]:
    r"""Convert a LaTeX article to Quarto markdown (.qmd).

    Preserves all body content; only structure is changed:
      - \section / \subsection / \subsubsection -> # / ## / ###
      - \maketitle, \begin{document}, \end{document} removed
    Everything between \begin{document} and \end{document} is retained.
    """
    original_word_count = len(tex_text.split())

    # Use shared utilities for metadata/body extraction
    title = extract_title(tex_text, fallback_title)

    # Extract abstract (Quarto-specific formatting)
    m_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, re.DOTALL)
    abstract = m_abs.group(1).strip() if m_abs else None

    body = extract_body(tex_text)

    # Clean document structure commands using shared utility
    body = clean_common_latex(body)

    # Remove abstract from body (already extracted)
    body = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", "", body, flags=re.DOTALL)

    # Handle \tableofcontents
    toc = bool(re.search(r"\\tableofcontents", body))
    body = re.sub(r"\\tableofcontents", "", body)

    # Remove \appendix command
    body = re.sub(r"\\appendix\b", "", body)

    # Use shared section conversion
    body = convert_sections_to_markdown(body)

    # Convert \appendix to Quarto appendix heading
    body = re.sub(r"\\appendix", "\n\n# Appendix {.appendix}\n\n", body)

    body = body.strip()

    # Build Quarto markdown with YAML front matter
    yaml = f'---\ntitle: "{title}"\nformat:\n  html:'
    if toc:
        yaml += "\n    toc: true"
    yaml += "\n"
    if abstract:
        indented_abstract = abstract.replace("\n", "\n  ")
        yaml += f"abstract: |\n  {indented_abstract}\n"
    yaml += "---\n\n"

    md = f"{yaml}{body}\n"
    md_word_count = len(md.split())
    return md, original_word_count, md_word_count


def main() -> None:
    """Main entry point for LaTeX to Quarto converter."""
    if len(sys.argv) > 1:
        input_paths = sys.argv[1:]
        tex_files = find_files_by_extension([".tex"], paths=input_paths)

        if not tex_files:
            sys.exit(1)
    else:
        tex_files = prompt_for_files()
        if not tex_files:
            sys.exit(0)

    for tex_path in tex_files:
        try:
            tex_text = tex_path.read_text(encoding="utf-8")
            fallback_title = tex_path.stem.replace("_", " ")
            md_text, _before_wc, _after_wc = latex_to_quarto_md(tex_text, fallback_title)
            qmd_path = tex_path.with_suffix(".qmd")
            qmd_path.write_text(md_text, encoding="utf-8")
            logger.info("Converted: %s -> %s", tex_path, qmd_path)
        except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
            logger.error("Failed to convert %s: %s", tex_path, e)


if __name__ == "__main__":
    main()
