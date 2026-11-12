#!/usr/bin/env python3
"""
Complete Book Compilation Script for "Control Is Motion"
Combines all chapters into a single comprehensive textbook.
"""

import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_SCRIPT_DIR = Path(__file__).resolve().parent


def extract_chapter_content(filepath: str) -> str:
    """Extract the content between \\begin{document} and \\end{document}"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Find the actual chapter content, skipping preamble
        start_idx = content.find("\\chapter{")
        if start_idx == -1:
            # Look for setcounter chapter
            start_idx = content.find("\\setcounter{chapter}")

        end_idx = content.find("\\end{document}")
        if start_idx != -1 and end_idx != -1:
            return content[start_idx:end_idx].strip()
        elif start_idx != -1:
            return content[start_idx:].strip()
        else:
            return ""
    except FileNotFoundError:
        return ""


_PREAMBLE = r"""\documentclass[12pt, openany]{book}

% ──────────────────────────────────────────────
% Packages
% ──────────────────────────────────────────────
\usepackage[margin=1in]{geometry}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{mathtools}
\usepackage{bm}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta, decorations.markings, calc, patterns, positioning}
\usepackage{tcolorbox}
\tcbuselibrary{theorems, breakable, skins}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{epigraph}
\usepackage{xcolor}
\usepackage{booktabs}

% ──────────────────────────────────────────────
% Colors
% ──────────────────────────────────────────────
\definecolor{chapblue}{RGB}{0, 70, 130}
\definecolor{accentred}{RGB}{180, 40, 40}
\definecolor{softgray}{RGB}{245, 245, 245}
\definecolor{trajgreen}{RGB}{30, 130, 60}
\definecolor{darkgold}{RGB}{160, 120, 20}
\definecolor{purplehaze}{RGB}{100, 40, 140}

% ──────────────────────────────────────────────
% Theorem environments
% ──────────────────────────────────────────────
\newtcbtheorem[number within=chapter]{principle}{Principle}{
  colback=chapblue!5, colframe=chapblue!80,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{princ}

\newtcbtheorem[number within=chapter]{keyidea}{Key Idea}{
  colback=accentred!5, colframe=accentred!70,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{idea}

\newtcbtheorem[number within=chapter]{example}{Example}{
  colback=softgray, colframe=black!40,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{ex}

\newtcbtheorem[number within=chapter]{definition}{Definition}{
  colback=darkgold!5, colframe=darkgold!80,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{def}

\newtcbtheorem[number within=chapter]{remark}{Remark}{
  colback=purplehaze!5, colframe=purplehaze!60,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{rem}

\newtcbtheorem[number within=chapter]{warning}{Warning}{
  colback=accentred!5, colframe=accentred!80,
  fonttitle=\bfseries, separator sign={.~},
  breakable
}{warn}

\theoremstyle{plain}
\newtheorem{proposition}{Proposition}[chapter]
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}

% ──────────────────────────────────────────────
% Chapter formatting
% ──────────────────────────────────────────────
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\color{chapblue}}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{-20pt}{30pt}

% ──────────────────────────────────────────────
% Header/Footer
% ──────────────────────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[RE]{\textit{Control Is Motion}}
\fancyhead[LO]{\textit{\nouppercase{\leftmark}}}
\renewcommand{\headrulewidth}{0.4pt}
\setlength{\headheight}{14.5pt}

% ──────────────────────────────────────────────
% Custom commands
% ──────────────────────────────────────────────
\newcommand{\state}{\bm{x}}
\newcommand{\control}{\bm{u}}
\newcommand{\traj}{\bm{\gamma}}
\newcommand{\manifold}{\mathcal{M}}
\newcommand{\configspace}{\mathcal{Q}}
\newcommand{\statespace}{\mathcal{X}}
\newcommand{\controlspace}{\mathcal{U}}
\newcommand{\tube}{\mathcal{T}}
\newcommand{\Reals}{\mathbb{R}}
\newcommand{\dd}{\mathrm{d}}
\newcommand{\dt}{\,\dd t}
\newcommand{\norm}[1]{\left\lVert #1 \right\rVert}
\newcommand{\inner}[2]{\left\langle #1,\, #2 \right\rangle}

% Additional commands for specific chapters
\newcommand{\tangent}{\bm{T}}
\newcommand{\normal}{\bm{N}}
\newcommand{\binormal}{\bm{B}}

% ──────────────────────────────────────────────
% Title Page
% ──────────────────────────────────────────────
\title{%
  {\Huge\bfseries\color{chapblue} Control Is Motion}\\[0.4cm]
  {\Large Geometry, Feasible Dynamics, and Robust Outcomes}\\[0.6cm]
  {\color{chapblue}\rule{\textwidth}{2pt}}
}
\author{{\Large D.\ Kraft}}
\date{}

\begin{document}

\maketitle
\thispagestyle{empty}
\cleardoublepage

% ──────────────────────────────────────────────
% Table of Contents
% ──────────────────────────────────────────────
\tableofcontents
\cleardoublepage

"""


_CHAPTER_FILES = [str(_SCRIPT_DIR / f"chapter{i}.tex") for i in range(1, 12)]


def create_complete_book() -> str:
    """Create a complete book from all chapter files"""

    book_content = _PREAMBLE

    for _, chapter_file in enumerate(_CHAPTER_FILES):
        logger.info(f"Processing {chapter_file}...")
        chapter_content = extract_chapter_content(chapter_file)
        if chapter_content:
            book_content += chapter_content + "\n\n"
        else:
            logger.info(f"Warning: Could not extract content from {chapter_file}")

    # Add closing
    book_content += r"""
\end{document}
"""

    # Write the complete book
    output_file = str(_SCRIPT_DIR / "Control_Is_Motion_Complete.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(book_content)

    logger.info(f"Complete book written to: {output_file}")
    return output_file


def compile_pdf(tex_file: str) -> str | None:
    """Compile the LaTeX file to PDF"""
    try:
        # Change to the directory containing the tex file
        tex_path = Path(tex_file)
        os.chdir(tex_path.parent)

        # Run pdflatex twice for proper cross-references
        for i in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path.name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.info(f"LaTeX compilation failed on run {i + 1}")
                logger.info("Error output:", result.stderr)
                logger.info("Standard output:", result.stdout)
                return None

        pdf_file = tex_path.with_suffix(".pdf")
        if pdf_file.exists():
            logger.info(f"PDF successfully created: {pdf_file}")
            return str(pdf_file)
        else:
            logger.info("PDF file not found after compilation")
            return None

    except (
        Exception
    ) as e:  # noqa: BLE001  # reason: catch-all exception handler for top-level guard
        logger.info(f"Error during compilation: {e}")
        return None


def create_summary() -> None:
    """Confirm the tracked book summary is present (maintained with the chapters)."""
    summary_path = _SCRIPT_DIR / "BOOK_SUMMARY.md"
    if summary_path.is_file():
        logger.info("Using tracked summary: %s", summary_path)
    else:
        logger.warning("BOOK_SUMMARY.md missing beside compile_book.py")


if __name__ == "__main__":
    logger.info("=== Control Is Motion - Complete Book Compilation ===\n")

    # Create the complete book
    tex_file = create_complete_book()

    # Try to compile to PDF (may fail if LaTeX not available)
    logger.info("\nAttempting PDF compilation...")
    pdf_file = compile_pdf(tex_file)

    # Create summary
    create_summary()

    logger.info("\n=== Compilation Complete ===")
    logger.info(f"LaTeX source: {tex_file}")
    if pdf_file:
        logger.info(f"PDF output: {pdf_file}")
    else:
        logger.info("PDF compilation failed - LaTeX source ready for external compilation")

    logger.info("\nThe complete textbook 'Control Is Motion' has been generated.")
    logger.info("This comprehensive work presents a new framework for nonlinear control")
    logger.info("theory focused on systems that move through the world.")
