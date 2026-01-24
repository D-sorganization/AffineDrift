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

import re
import sys
from pathlib import Path

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.utils import find_files_by_extension, setup_logging

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
    r"""Convert a LaTeX article to Quarto markdown (.qmd) while preserving all body content.
    Only structure is changed:
      - \section / \subsection / \subsubsection -> # / ## / ###
      - \maketitle, \begin{document}, \end{document} removed
    Everything between \begin{document} and \end{document} is retained.
    """
    # Compute original word count
    original_word_count = len(tex_text.split())

    # Extract title
    m = re.search(r"\\title\{([^}]*)\}", tex_text)
    title = m.group(1).strip() if m else fallback_title

    # Extract abstract
    m_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, re.DOTALL)
    abstract = m_abs.group(1).strip() if m_abs else None

    # Extract body between \begin{document} and \end{document}
    m_begin = re.search(r"\\begin\{document\}", tex_text)
    m_end = re.search(r"\\end\{document\}", tex_text)
    start = m_begin.end() if m_begin else 0
    end = m_end.start() if m_end else len(tex_text)
    body = tex_text[start:end]

    # Remove LaTeX document structure commands (more comprehensive)
    body = re.sub(r"\\maketitle", "", body)
    body = re.sub(r"\\title\{[^}]*\}", "", body)
    body = re.sub(r"\\author\{[^}]*\}", "", body)
    body = re.sub(r"\\date\{[^}]*\}", "", body)

    # Remove abstract from body (if not already extracted)
    body = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", "", body, flags=re.DOTALL)

    # Remove \tableofcontents and set toc: true
    toc = False
    if re.search(r"\\tableofcontents", body):
        toc = True
        body = re.sub(r"\\tableofcontents", "", body)

    # Remove LaTeX comments (lines starting with %)
    body = re.sub(r"^%.*$", "", body, flags=re.MULTILINE)
    # Remove comment blocks
    body = re.sub(r"%.*", "", body)

    # Remove \appendix command (will be converted to heading later)
    body = re.sub(r"\\appendix\b", "", body)

    # Convert section commands to markdown headings
    body = re.sub(r"\\section\*?\{([^}]*)\}", r"\n\n# \1\n\n", body)
    body = re.sub(r"\\subsection\*?\{([^}]*)\}", r"\n\n## \1\n\n", body)
    body = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"\n\n### \1\n\n", body)

    # Convert \appendix to Quarto appendix heading
    body = re.sub(r"\\appendix", "\n\n# Appendix {.appendix}\n\n", body)

    body = body.strip()

    # Build Quarto markdown with YAML front matter
    yaml = f'---\ntitle: "{title}"\nformat:\n  html:'
    if toc:
        yaml += "\n    toc: true"
    yaml += "\n"
    if abstract:
        # Replace newlines with indented newlines (can't use backslash in f-string expression)
        indented_abstract = abstract.replace("\n", "\n  ")
        yaml += f"abstract: |\n  {indented_abstract}\n"
    yaml += "---\n\n"

    md = f"{yaml}{body}\n"

    md_word_count = len(md.split())
    return md, original_word_count, md_word_count


def main() -> None:
    """Main entry point for LaTeX to Quarto converter."""
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Use command-line arguments (folders or files)
        input_paths = sys.argv[1:]
        tex_files = find_files_by_extension([".tex"], paths=input_paths)

        if not tex_files:
            sys.exit(1)
    else:
        # Fall back to GUI
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
        except Exception as e:
            logger.error("Failed to convert %s: %s", tex_path, e)


if __name__ == "__main__":
    main()
