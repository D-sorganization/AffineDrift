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
        self.template_file = template_file

    @staticmethod
    def read_latex_file(filepath: str | Path) -> str:
        """Read LaTeX file content."""
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    def convert_latex_to_html(self, latex_content: str) -> str:
        """Convert LaTeX content to HTML.

        Applies shared utilities for sections, text formatting, lists,
        references, quotes, and URLs. Then applies HTML-specific conversions
        for equations, custom environments, and paragraphs.
        """
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
        """Clean HTML-specific LaTeX commands.

        Applies shared cleanup (comments, labels, spacing) via
        ``clean_common_latex``, then handles HTML-specific environments
        like keypoint boxes, limitation boxes, and tikz.
        """
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

    def create_html_page(self, title: str, content: str, description: str = "") -> str:
        """Create complete HTML page with AffineDrift template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title} - AffineDrift</title>
    <!-- Google Fonts - Playfair Display -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap"
          rel="stylesheet">
    <!-- Preconnect to CDN for faster loading -->
    <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin="anonymous">
    <link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
    <link rel="stylesheet" href="../../../styles.css">
    <link rel="icon" type="image/x-icon" href="../../../favicon.ico">
    <link rel="icon" type="image/x-icon" sizes="16x16" href="../../../favicon.ico">
    <link rel="icon" type="image/x-icon" sizes="32x32" href="../../../favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="../../../logo/Logo Transparent/1.png">
    <link rel="icon" type="image/png" sizes="192x192" href="../../../logo/Logo Transparent/1.png">
    <link rel="icon" type="image/png" sizes="512x512" href="../../../logo/Logo Transparent/1.png">
    <meta name="theme-color" content="#0f4c75">
    <!-- MathJax for mathematical notation -->
    <script>
      window.MathJax = {{
        tex: {{
          inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
          displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
          processEscapes: true,
          processEnvironments: true
        }},
        startup: {{
          ready: () => {{
            MathJax.startup.defaultReady();
          }}
        }}
      }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        .equation {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            border-left: 4px solid #3282b8;
            overflow-x: auto;
        }}
        .article-content h2 {{
            color: #0f4c75;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e7f3ff;
        }}
        .article-content h3 {{
            color: #3282b8;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }}
        .article-content h4 {{
            color: #3282b8;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .article-content p {{
            margin-bottom: 1.25rem;
            line-height: 1.8;
        }}
        .article-content ul, .article-content ol {{
            margin-bottom: 1.5rem;
            line-height: 1.8;
        }}
        .article-content li {{
            margin-bottom: 0.5rem;
        }}
        .article-content code {{
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .abstract-section {{
            background: #e7f3ff;
            padding: 2rem;
            border-radius: 8px;
            margin: 2rem 0;
            border-left: 4px solid #3282b8;
        }}
        .abstract-section h2 {{
            margin-top: 0;
            color: #0f4c75;
        }}
        .keypoint-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 8px;
        }}
        .limitation-box {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <header>
        <nav class="top-nav">
            <div class="container">
                <a href="../../../index.html" class="logo-link">
                    <img src="../../../logo/Logo Transparent/1.png"
                         alt="AffineDrift Logo" class="logo-img">
                </a>
                <ul class="nav-links">
                    <li><a href="../../../index.html">Affine Drift</a></li>
                    <li><a href="../../../articles.html">Articles</a></li>
                    <li><a href="../../../research-reviews.html">Reviews</a></li>
                    <li><a href="../../../resources.html">Resources</a></li>
                    <li><a href="../../../contact.html">Contact</a></li>
                    <li><a href="../../../about.html">About</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <div class="layout-wrapper">
        <aside class="sidebar" id="history-sidebar">
            <nav class="sidebar-nav">
                <div class="sidebar-section">
                    <h3 class="sidebar-heading">Recent Pages</h3>
                    <ul class="sidebar-links" id="history-list">
                        <li class="history-empty">No recent pages yet</li>
                    </ul>
                </div>
            </nav>
        </aside>

        <main class="main-content">
            <section class="page-header">
                <div class="container">
                    <h1>{title}</h1>
                </div>
            </section>

            <section class="article-section">
                <div class="container">
                    <article class="article-content">
{content}
                    </article>
                </div>
            </section>
        </main>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2025 AffineDrift. Exploring the mathematics of motion.</p>
            <p class="footer-tagline">The past shapes the present</p>
        </div>
    </footer>

    <script src="../../../script.js"></script>
</body>
</html>
"""

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
