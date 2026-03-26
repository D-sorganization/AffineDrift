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


def create_complete_book() -> str:
    """Create a complete book from all chapter files"""

    # LaTeX preamble
    preamble = r"""\documentclass[12pt, openany]{book}

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
  {\Large A New Framework for Nonlinear Systems\\
  That Move Through the World}\\[0.6cm]
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

    # Chapter files in order
    chapter_files = [
        "/mnt/project/chapter1.tex",
        "/mnt/project/chapter2.tex",
        "/mnt/project/chapter3.tex",
        "/mnt/project/chapter4.tex",
        "/mnt/project/chapter5.tex",
        "/mnt/project/chapter6.tex",
        "/mnt/project/chapter7.tex",
        "/mnt/project/chapter8.tex",
        "/mnt/project/chapter9.tex",
        "/mnt/project/chapter10.tex",
        "/mnt/project/chapter11.tex",
    ]

    # Build the complete book content
    book_content = preamble

    for _, chapter_file in enumerate(chapter_files):
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
    output_file = "/home/claude/Control_Is_Motion_Complete.tex"
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

    except Exception as e:  # noqa: BLE001
        logger.info(f"Error during compilation: {e}")
        return None


def create_summary() -> None:
    """Create a summary of what was accomplished"""
    summary = """
# Control Is Motion - Complete Textbook

## Book Overview
This textbook presents a revolutionary framework for nonlinear control theory,
shifting from the classical "setpoint control" paradigm to a "trajectory control"
approach specifically designed for systems that move through the world.

## Key Themes
- **Control is Motion, not Destination**: The fundamental insight that control
  systems should be designed around trajectories, not fixed points
- **Moving Target Systems**: Systems whose objectives are defined by kinematics
  at specific intersections, independent of timing
- **Geometric Approach**: Treating trajectories as geometric objects with
  intrinsic curvature and structure
- **Underactuation as Advantage**: Exploiting passive dynamics rather than
  fighting them

## Chapter Summary

### Chapter 1: Throwing Away the Target
- Introduces the central thesis: "Control is motion"
- Contrasts classical setpoint control with trajectory control
- Defines moving target systems using the golf swing as primary example
- Establishes the philosophical and mathematical foundation

### Chapter 2: Curves in State Space
- Mathematical treatment of trajectories as geometric curves
- Arc length parameterization and path-timing separation
- Curvature, torsion, and their relationship to control difficulty
- Frenet-Serret frames and coordinate-independent descriptions

### Chapter 3: Configuration Manifolds
- Beyond Euclidean state spaces: Lie groups and curved manifolds
- Special treatment of rotational motion and SO(3)
- Riemannian metrics derived from kinetic energy
- Constraints and submanifolds in mechanical systems

### Chapter 4: Orbital Stability and Transverse Linearization
- Rethinking stability for moving systems
- Orbital stability vs. classical Lyapunov stability
- Transverse linearization and moving Poincaré sections
- Floquet theory for periodic motions

### Chapter 5: Underactuation and Passive Dynamics
- Embracing underactuation as a design principle
- Zero dynamics and the structure of underactuated systems
- The whip effect and sequential energy transfer
- Applications to the golf swing kinetic chain

### Chapter 6: Trajectory Optimization
- Moving target optimal control problems
- Direct collocation methods for complex systems
- Multi-phase optimization and cost function design
- From optimization to implementable trajectories

### Chapter 7: Funnel Synthesis
- Beyond point tracking: finite-time guarantees
- Forward invariant funnels and barrier functions
- Sum-of-squares programming for funnel computation
- Robust funnels under model uncertainty

### Chapter 8: Phase-Variable Control
- Decoupling path shape from timing
- Virtual constraints and hybrid zero dynamics
- Central pattern generators as phase oscillators
- Applications to locomotion and rhythmic motions

### Chapter 9: Stochastic Trajectories and Motor Variability
- Signal-dependent noise in biological actuators
- Minimum-variance theory of human movement
- Why optimal trajectories are naturally smooth
- Covariance steering for robust trajectory design

### Chapter 10: Learning to Move
- Iterative learning control for trajectory improvement
- Policy search and trajectory libraries
- Maintaining stability while adapting performance
- Applications to athletic skill development

### Chapter 11: Case Study - The Complete Golf Swing
- Full application of the entire framework
- 15-DOF musculoskeletal model optimization
- Funnel synthesis for the complete swing
- Integration of all theoretical concepts

## Technical Features
- Rigorous mathematical treatment with geometric insight
- Extensive use of examples from athletics and robotics
- Practical algorithms and computational methods
- End-of-chapter exercises ranging from conceptual to computational
- Beautiful visual presentations using TikZ graphics

## Target Audience
- Graduate students in robotics, control theory, and biomechanics
- Researchers working on underactuated systems and trajectory control
- Engineers designing systems for complex motions
- Anyone interested in the intersection of control theory and human movement

## Unique Contributions
This textbook is the first comprehensive treatment of trajectory-based control
theory for moving target systems. It bridges classical control theory with
modern geometric methods, providing both theoretical foundations and practical
tools for designing controllers for systems that must move through the world
with purpose and precision.
"""

    with open("/home/claude/BOOK_SUMMARY.md", "w") as f:
        f.write(summary)

    logger.info("Book summary created: BOOK_SUMMARY.md")


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
