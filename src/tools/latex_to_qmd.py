#!/usr/bin/env python3
"""LaTeX to Quarto (.qmd) Converter for AffineDrift
Converts LaTeX article files to Quarto Markdown with preserved equations.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path


from src.tools.utils import setup_logging_with_timestamp

logger = setup_logging_with_timestamp(__name__)


class LaTeXToQuartoConverter:
    """Converter class for handling LaTeX to Quarto transformation."""

    def __init__(self) -> None:
        """Initialize converter."""
        # Converter initialized with default settings

    def read_latex_file(self, filepath: str | Path) -> str:
        """Read LaTeX file content."""
        try:
            with open(filepath, encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error reading file {filepath}: {e}")
            raise

    def extract_metadata(self, latex_content: str) -> dict[str, str]:
        """Extract title, author, and other metadata from LaTeX."""
        metadata = {}

        # Extract title
        title_match = re.search(r"\\title\{([^}]+)\}", latex_content, re.DOTALL)
        if title_match:
            title = title_match.group(1)
            # Clean LaTeX commands
            title = re.sub(r"\\textbf\{([^}]+)\}", r"\1", title)
            title = re.sub(r"\\\\\[[^\]]+\]", " ", title)
            title = re.sub(r"\\\\", " ", title)
            metadata["title"] = title.strip()
        else:
            metadata["title"] = "Untitled Article"

        # Extract author if present
        author_match = re.search(r"\\author\{([^}]+)\}", latex_content, re.DOTALL)
        if author_match:
            metadata["author"] = author_match.group(1).strip()
        else:
            metadata["author"] = "AffineDrift"

        # Add date
        metadata["date"] = date.today().strftime("%Y-%m-%d")

        return metadata

    def extract_body(self, latex_content: str) -> str:
        r"""Extract content between \begin{document} and \end{document}."""
        doc_match = re.search(r"\\begin\{document\}(.+)\\end\{document\}", latex_content, re.DOTALL)
        content = doc_match.group(1) if doc_match else latex_content

        # Remove \maketitle
        return re.sub(r"\\maketitle", "", content)

    def convert_sections(self, content: str) -> str:
        """Convert LaTeX sections to Markdown headers."""
        # Sections
        content = re.sub(r"\\section\{([^}]+)\}", r"## \1", content)
        content = re.sub(r"\\subsection\{([^}]+)\}", r"### \1", content)
        content = re.sub(r"\\subsubsection\{([^}]+)\}", r"#### \1", content)
        content = re.sub(r"\\paragraph\{([^}]+)\}", r"##### \1", content)
        return re.sub(r"\\subparagraph\{([^}]+)\}", r"###### \1", content)

    def convert_text_formatting(self, content: str) -> str:
        """Convert LaTeX text formatting to Markdown."""
        # Bold
        content = re.sub(r"\\textbf\{([^}]+)\}", r"**\1**", content)
        # Italic
        content = re.sub(r"\\textit\{([^}]+)\}", r"*\1*", content)
        content = re.sub(r"\\emph\{([^}]+)\}", r"*\1*", content)
        # Code
        content = re.sub(r"\\texttt\{([^}]+)\}", r"`\1`", content)
        # Quotes
        content = re.sub(r"``", r'"', content)
        return re.sub(r"''", r'"', content)

    def convert_lists(self, content: str) -> str:
        """Convert LaTeX lists to Markdown lists."""

        # Itemize (unordered)
        def replace_itemize(match: re.Match[str]) -> str:
            """Replace itemize environment with Markdown unordered list."""
            items = match.group(1)
            # Replace \item with -
            items = re.sub(r"\\item\s+", "\n- ", items)
            items = re.sub(r"\\item\s*$", "\n- ", items, flags=re.MULTILINE)
            return items.strip()

        content = re.sub(
            r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
            replace_itemize,
            content,
            flags=re.DOTALL,
        )

        # Enumerate (ordered)
        def replace_enumerate(match: re.Match[str]) -> str:
            """Replace enumerate environment with Markdown ordered list."""
            items = match.group(1)
            # Replace \item with numbered list
            item_count = [0]  # Use list to make it mutable in nested function

            def number_item(m: re.Match[str]) -> str:
                """Number items in enumerate list."""
                item_count[0] += 1
                return f"\n{item_count[0]}. "

            items = re.sub(r"\\item\s+", number_item, items)
            return items.strip()

        return re.sub(
            r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}",
            replace_enumerate,
            content,
            flags=re.DOTALL,
        )

    def convert_environments(self, content: str) -> str:
        """Convert special LaTeX environments."""
        # Abstract
        content = re.sub(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
            r"::: {.abstract-section}\n## Abstract\n\n\1\n\n:::",
            content,
            flags=re.DOTALL,
        )

        # Key points
        content = re.sub(
            r"\\begin\{keypoint\}(?:\[[^\]]*\])?(.*?)\\end\{keypoint\}",
            r"::: {.keypoint-box}\n**Key Point:** \1\n:::",
            content,
            flags=re.DOTALL,
        )

        # Limitations
        content = re.sub(
            r"\\begin\{limitation\}(?:\[[^\]]*\])?(.*?)\\end\{limitation\}",
            r"::: {.limitation-box}\n**Fundamental Limitation:** \1\n:::",
            content,
            flags=re.DOTALL,
        )

        # Quotes
        return re.sub(r"\\begin\{quote\}(.*?)\\end\{quote\}", r"> \1", content, flags=re.DOTALL)

    def convert_equations(self, content: str) -> str:
        """Convert LaTeX equations - Quarto supports them natively!."""
        # Display equations - keep as-is, Quarto understands them
        # Just ensure they're on their own lines

        # align environments - keep as-is
        content = re.sub(r"\\begin\{align\}", r"\n$$\n\\begin{align}", content)
        content = re.sub(r"\\end\{align\}", r"\\end{align}\n$$\n", content)

        # equation environments - keep as-is
        content = re.sub(r"\\begin\{equation\}", r"\n$$", content)
        return re.sub(r"\\end\{equation\}", r"$$\n", content)

    def convert_figures(self, content: str) -> str:
        """Convert LaTeX figures to Quarto format."""

        # Remove complex figure environments but preserve caption info
        def replace_figure(match: re.Match[str]) -> str:
            """Replace LaTeX figure environment with Quarto figure syntax."""
            fig_content = match.group(1)

            # Try to extract caption
            caption_match = re.search(r"\\caption\{([^}]+)\}", fig_content)
            caption = caption_match.group(1) if caption_match else ""

            if caption:
                return f"\n\n[Figure: {caption}]\n\n"
            return "\n\n[Figure]\n\n"

        content = re.sub(
            r"\\begin\{figure\}(.*?)\\end\{figure\}",
            replace_figure,
            content,
            flags=re.DOTALL,
        )

        # Remove tikzpicture environments
        return re.sub(
            r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
            "[Figure: TikZ diagram - see PDF version]",
            content,
            flags=re.DOTALL,
        )

    def convert_references(self, content: str) -> str:
        """Convert LaTeX cross-references."""
        # Convert \ref and \cref to Quarto format
        content = re.sub(r"\\cref\{([^}]+)\}", r"[@\1]", content)
        content = re.sub(r"\\ref\{([^}]+)\}", r"[@\1]", content)

        # Convert \label to Quarto format
        content = re.sub(r"\\label\{eq:([^}]+)\}", r"{#eq-\1}", content)
        content = re.sub(r"\\label\{fig:([^}]+)\}", r"{#fig-\1}", content)
        content = re.sub(r"\\label\{sec:([^}]+)\}", r"{#sec-\1}", content)
        return re.sub(r"\\label\{([^}]+)\}", r"{#\1}", content)

    def convert_links(self, content: str) -> str:
        """Convert LaTeX URLs and hyperlinks to Markdown."""
        # \url{...}
        content = re.sub(r"\\url\{([^}]+)\}", r"<\1>", content)
        # \href{url}{text}
        return re.sub(r"\\href\{([^}]+)\}\{([^}]+)\}", r"[\2](\1)", content)

    def clean_latex_commands(self, content: str) -> str:
        """Remove or clean remaining LaTeX commands."""
        # Remove comments
        content = re.sub(r"%.*$", "", content, flags=re.MULTILINE)

        # Remove vspace, hspace
        content = re.sub(r"\\[vh]space\*?\{[^}]+\}", "", content)

        # Remove font size commands
        content = re.sub(
            r"\\(small|large|Large|huge|Huge|tiny|footnotesize|scriptsize|normalsize)",
            "",
            content,
        )

        # Custom commands - convert to bold
        content = re.sub(r"\\bvec\{([^}]+)\}", r"**\1**", content)
        content = re.sub(r"\\(Feq|Ceq|Rdrift|Rinput)", r"**\1**", content)

        # Remove table environments (not converting tables in this version)
        content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "[Table]", content, flags=re.DOTALL)
        content = re.sub(
            r"\\begin\{tabular\}.*?\\end\{tabular\}",
            "[Table]",
            content,
            flags=re.DOTALL,
        )

        # Remove theorem/definition environments
        return re.sub(
            r"\\begin\{(theorem|definition|proposition|lemma)\}(.*?)\\end\{\1\}",
            r"\n\n**\1:** \2\n\n",
            content,
            flags=re.DOTALL,
        )

    def create_frontmatter(self, metadata: dict[str, str]) -> str:
        """Create Quarto YAML frontmatter."""
        frontmatter = "---\n"
        frontmatter += f'title: "{metadata["title"]}"\n'
        frontmatter += f'author: "{metadata["author"]}"\n'
        frontmatter += f'date: "{metadata["date"]}"\n'
        frontmatter += """format:
  html:
    toc: true
    toc-depth: 3
    number-sections: false
    code-fold: true
---

"""
        return frontmatter

    def convert_to_qmd(self, latex_content: str) -> str:
        """Main conversion pipeline."""
        # Extract metadata
        metadata = self.extract_metadata(latex_content)

        # Extract body
        content = self.extract_body(latex_content)

        # Apply conversions in order
        content = self.convert_sections(content)
        content = self.convert_environments(content)
        content = self.convert_equations(content)
        content = self.convert_lists(content)
        content = self.convert_figures(content)
        content = self.convert_text_formatting(content)
        content = self.convert_references(content)
        content = self.convert_links(content)
        content = self.clean_latex_commands(content)

        # Clean up extra whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Create frontmatter
        frontmatter = self.create_frontmatter(metadata)

        return frontmatter + content.strip() + "\n"

    def convert_file(
        self, input_file: str | Path, output_file: str | Path | None = None
    ) -> Path | None:
        """Convert a LaTeX file to Quarto .qmd."""
        if output_file is None:
            output_file = Path(input_file).with_suffix(".qmd")

        logger.info(f"Converting {input_file} to {output_file}...")

        # Read LaTeX content
        try:
            latex_content = self.read_latex_file(input_file)
        except (re.error, ValueError):
            return None  # Error logged in read_latex_file

        # Convert to Quarto
        try:
            qmd_content = self.convert_to_qmd(latex_content)
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error during conversion: {e}")
            raise

        # Write output
        output_path = Path(output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(qmd_content)
            logger.info(f"Successfully converted {input_file}")
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise

        return output_path


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        logger.error("Usage: latex_to_qmd.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    converter = LaTeXToQuartoConverter()
    try:
        converter.convert_file(input_file, output_file)
    except (FileNotFoundError, PermissionError, OSError):
        sys.exit(1)


if __name__ == "__main__":
    main()
