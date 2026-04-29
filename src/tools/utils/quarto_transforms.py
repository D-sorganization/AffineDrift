"""Quarto-specific LaTeX-to-Markdown transformation functions.

Extracted from ``latex_to_qmd.py`` so they can be reused by other
conversion pipelines or tested independently.
"""

from __future__ import annotations

import re


def convert_quarto_environments(content: str) -> str:
    """Convert special LaTeX environments to Quarto callout/div syntax."""
    content = re.sub(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        r"::: {.abstract-section}\n## Abstract\n\n\1\n\n:::",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"\\begin\{keypoint\}(?:\[[^\]]*\])?(.*?)\\end\{keypoint\}",
        r"::: {.keypoint-box}\n**Key Point:** \1\n:::",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"\\begin\{limitation\}(?:\[[^\]]*\])?(.*?)\\end\{limitation\}",
        r"::: {.limitation-box}\n**Fundamental Limitation:** \1\n:::",
        content,
        flags=re.DOTALL,
    )
    return re.sub(r"\\begin\{quote\}(.*?)\\end\{quote\}", r"> \1", content, flags=re.DOTALL)


def convert_quarto_equations(content: str) -> str:
    """Convert LaTeX equation environments to Quarto-native dollar-sign syntax."""
    content = re.sub(r"\\begin\{align\}", r"\n$$\n\\begin{align}", content)
    content = re.sub(r"\\end\{align\}", r"\\end{align}\n$$\n", content)
    content = re.sub(r"\\begin\{equation\}", r"\n$$", content)
    return re.sub(r"\\end\{equation\}", r"$$\n", content)


def _replace_figure(match: re.Match[str]) -> str:
    """Replace a single LaTeX figure environment with Quarto figure syntax."""
    fig_content = match.group(1)
    caption_match = re.search(r"\\caption\{([^}]+)\}", fig_content)
    caption = caption_match.group(1) if caption_match else ""
    if caption:
        return f"\n\n[Figure: {caption}]\n\n"
    return "\n\n[Figure]\n\n"


def convert_quarto_figures(content: str) -> str:
    """Convert LaTeX figure and tikzpicture environments to Quarto placeholders."""
    content = re.sub(
        r"\\begin\{figure\}(.*?)\\end\{figure\}",
        _replace_figure,
        content,
        flags=re.DOTALL,
    )
    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        "[Figure: TikZ diagram - see PDF version]",
        content,
        flags=re.DOTALL,
    )


def convert_quarto_references(content: str) -> str:
    r"""Convert LaTeX \ref, \cref, \label to Quarto cross-reference format."""
    content = re.sub(r"\\cref\{([^}]+)\}", r"[@\1]", content)
    content = re.sub(r"\\ref\{([^}]+)\}", r"[@\1]", content)
    content = re.sub(r"\\label\{eq:([^}]+)\}", r"{#eq-\1}", content)
    content = re.sub(r"\\label\{fig:([^}]+)\}", r"{#fig-\1}", content)
    content = re.sub(r"\\label\{sec:([^}]+)\}", r"{#sec-\1}", content)
    return re.sub(r"\\label\{([^}]+)\}", r"{#\1}", content)


def clean_quarto_latex_commands(content: str) -> str:
    """Remove or convert Quarto-specific custom LaTeX commands."""
    content = re.sub(r"\\bvec\{([^}]+)\}", r"**\1**", content)
    content = re.sub(r"\\(Feq|Ceq|Rdrift|Rinput)", r"**\1**", content)
    content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "[Table]", content, flags=re.DOTALL)
    content = re.sub(
        r"\\begin\{tabular\}.*?\\end\{tabular\}",
        "[Table]",
        content,
        flags=re.DOTALL,
    )
    return re.sub(
        r"\\begin\{(theorem|definition|proposition|lemma)\}(.*?)\\end\{\1\}",
        r"\n\n**\1:** \2\n\n",
        content,
        flags=re.DOTALL,
    )


def create_quarto_frontmatter(metadata: dict[str, str]) -> str:
    """Create Quarto YAML frontmatter from a metadata dictionary."""
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


def convert_quarto_sections(content: str) -> str:
    """Convert LaTeX paragraph/subparagraph to Markdown h5/h6 headings."""
    content = re.sub(r"\\paragraph\{([^}]+)\}", r"##### \1", content)
    return re.sub(r"\\subparagraph\{([^}]+)\}", r"###### \1", content)
