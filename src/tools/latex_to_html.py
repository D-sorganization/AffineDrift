#!/usr/bin/env python3
"""LaTeX to HTML Converter for AffineDrift.

Converts LaTeX article files to HTML with MathJax rendering.
Uses shared LaTeX parsing utilities from ``src.tools.utils.latex_utils``
to avoid duplicated logic (DRY — Phase 2 consolidation).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from src.tools.utils import setup_logging
from src.tools.utils.latex_utils import (
    clean_common_latex,
    convert_lists_to_html,
    convert_quotes,
    convert_references,
    convert_sections_to_html,
    convert_text_formatting_to_html,
    convert_urls_to_html,
    extract_body,
    extract_title,
)

logger = setup_logging(__name__)


class LaTeXToHTMLConverter:
    """Converter class for handling LaTeX to HTML transformation.

    Delegates shared LaTeX parsing to ``latex_utils`` and retains
    HTML-specific conversion (equations, custom environments, template).
    """

    def __init__(self, template_file: str | Path | None = None) -> None:
        """Initialize converter with optional custom template."""
        if template_file is None:
            # Try to find a default template
            default_template = (
                Path(__file__).parent.parent.parent / "_templates" / "latex_article.html"
            )
            if default_template.exists():
                template_file = default_template
        self.template_file = template_file

    @staticmethod
    def read_latex_file(filepath: str | Path) -> str:
        """Read LaTeX file content."""
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    def convert_latex_to_html(self, latex_content: str) -> str:
        """Convert LaTeX content to HTML."""
        html = latex_content

        # Convert abstract environment (HTML-specific styling)
        html = re.sub(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
            r'<div class="abstract-section">\n<h2>Abstract</h2>\n<p>\1</p>\n</div>',
            html,
            flags=re.DOTALL,
        )

        # --- Shared conversions (from latex_utils) ---
        html = convert_sections_to_html(html)
        html = convert_text_formatting_to_html(html)
        html = convert_lists_to_html(html)
        html = self.convert_equations(html)

        # Convert align environments
        html = re.sub(r"\\begin\{align\}", r"\\begin{align}", html)
        html = re.sub(r"\\end\{align\}", r"\\end{align}", html)

        html = convert_references(html)
        html = convert_quotes(html)
        html = convert_urls_to_html(html)

        # --- HTML-specific cleanup ---
        html = self._clean_html_specific(html)

        # Convert paragraphs
        return self.convert_paragraphs(html)

    def convert_equations(self, content: str) -> str:
        """Convert LaTeX equation environments to MathJax-friendly format."""
        # Display equations
        content = re.sub(
            r"\\begin\{equation\}(.*?)\\end\{equation\}",
            r'<div class="equation">\n\\[\1\\]\n</div>',
            content,
            flags=re.DOTALL,
        )

        # Already wrapped equations
        return re.sub(
            r"\\\[(.*?)\\\]",
            r'<div class="equation">\n\\[\1\\]\n</div>',
            content,
            flags=re.DOTALL,
        )

    def convert_paragraphs(self, content: str) -> str:
        """Convert LaTeX paragraphs to HTML paragraphs."""
        lines = content.split("\n\n")
        result = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip if already wrapped in HTML tags
            if line.startswith("<") and (line.startswith(("<h", "<div", "<ul", "<ol", "<figure"))):
                result.append(line)
            elif line:
                result.append(f"<p>\n{line}\n</p>")

        return "\n\n".join(result)

    def _clean_html_specific(self, content: str) -> str:
        """Clean HTML-specific LaTeX commands."""
        # Shared cleanup: comments, labels, spacing, document structure
        content = clean_common_latex(content)

        # Handle special colored boxes — convert to styled divs
        content = re.sub(
            r"\\begin\{keypoint\}(?:\[[^\]]*\])?(.*?)\\end\{keypoint\}",
            r'<div class="keypoint-box"><strong>Key Point:</strong>\1</div>',
            content,
            flags=re.DOTALL,
        )
        content = re.sub(
            r"\\begin\{limitation\}(?:\[[^\]]*\])?(.*?)\\end\{limitation\}",
            r'<div class="limitation-box"><strong>Fundamental Limitation:</strong>\1</div>',
            content,
            flags=re.DOTALL,
        )

        # Remove figure, table, theorem, definition environments
        content = re.sub(
            r"\\begin\{(figure|table|theorem|definition)\}.*?\\end\{\1\}",
            "",
            content,
            flags=re.DOTALL,
        )

        # Remove graphics/figure commands
        content = re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^}]+\}", "[Figure]", content)
        content = re.sub(r"\\caption\{[^}]+\}", "", content)

        # Convert custom commands to styled text
        content = re.sub(r"\\bvec\{([^}]+)\}", r"<strong>\1</strong>", content)
        content = re.sub(r"\\(Feq|Ceq|Rdrift|Rinput)", r"<strong>\1</strong>", content)

        # Remove tikz and pgfplots entirely
        return re.sub(
            r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
            "[Figure: See PDF version]",
            content,
            flags=re.DOTALL,
        )

    def _get_template(self) -> str:
        """Read the HTML template from file or return a fallback."""
        if self.template_file and Path(self.template_file).exists():
            try:
                with open(self.template_file, encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read template file: {e}")

        # Fallback template if file is missing
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>{{title}}</title>
</head>
<body>
    <h1>{{title}}</h1>
    <article>{{content}}</article>
</body>
</html>"""

    def create_html_page(self, title: str, content: str, description: str = "") -> str:
        """Create complete HTML page using the external template."""
        template = self._get_template()

        # Simple placeholder replacement
        html_out = template.replace("{{title}}", title)
        html_out = html_out.replace("{{content}}", content)
        html_out = html_out.replace("{{description}}", description)

        return html_out

    def convert_file(
        self,
        input_file: str | Path,
        output_file: str | Path | None = None,
    ) -> str:
        """Convert a LaTeX file to HTML."""
        if output_file is None:
            output_file = Path(input_file).with_suffix(".html")

        # Read LaTeX content
        latex_content = self.read_latex_file(input_file)

        # Extract title and body using shared utilities
        title = extract_title(latex_content)
        content = extract_body(latex_content)

        # Convert to HTML
        html_content = self.convert_latex_to_html(content)

        # Create full HTML page
        full_html = self.create_html_page(title, html_content, description=title)

        # Write output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_html)

        logger.info("Converted %s -> %s", input_file, output_file)
        return str(output_file)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        logger.error("Usage: python latex_to_html.py <input.tex> [output.html]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        logger.error("File not found: %s", input_file)
        sys.exit(1)

    converter = LaTeXToHTMLConverter()
    converter.convert_file(input_file, output_file)


if __name__ == "__main__":
    main()
