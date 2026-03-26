# Tangent-Space Methods for Nonlinear Control and Biomechanics — Manuscripts

## Purpose

Canonical LaTeX manuscript source for the multi-volume textbook series "Tangent-Space Methods for Nonlinear Control and Biomechanics" (formerly "The Geometry of Motion").

## Directory Structure

```
The_Geometry_of_Motion/
├── Volume_0/             — Mathematical Primer (LaTeX source)
├── Volume_I/             — Core mechanics (LaTeX source)
│   └── chapters/         — Individual chapter .tex files (canonical)
├── Volume_II/            — Advanced topics (LaTeX source)
├── quarto/               — Quarto/website mirror of chapter content
│   ├── index.qmd         — Book index page
│   ├── ch01_foundations.qmd ... ch08_applications.qmd
│   └── vol0_*.qmd        — Volume 0 chapters
├── geometry_of_motion.bib  — Shared bibliography
├── geometry_of_motion.sty  — Shared LaTeX style
└── compile_series.bat    — Build script for full series
```

## LaTeX vs. Quarto: Two Formats

This directory contains **two parallel representations** of the same content:

| Format              | Location                                 | Purpose               | Canonical?               |
| ------------------- | ---------------------------------------- | --------------------- | ------------------------ |
| **LaTeX** (`.tex`)  | `Volume_I/chapters/`, `Volume_II/`, etc. | Print/PDF typesetting | **Yes** — primary source |
| **Quarto** (`.qmd`) | `quarto/`                                | Website rendering     | Derived/mirror           |

The `.qmd` files in `quarto/` are website-adapted versions of the LaTeX chapters. When content differs, the LaTeX source is authoritative. A `convert_tex_to_qmd.py` script in `quarto/` can help regenerate the Quarto versions from LaTeX source, but the conversion is not fully automated and requires manual review.

**Relationship to AffineDrift website:** The GoM Quarto files are part of the website (rendered by Quarto). The LaTeX files are not rendered to HTML — they are used to generate PDFs for the textbook.

## Implementation Status

- Volume-level directories are present and compile through CI workflows.
- Shared bibliography and chapter structure are in active development.

## Known Gaps

- Cross-volume style normalization and some chapter expansion tasks are still open.
- The `quarto/` mirror may lag behind LaTeX chapters — check both before citing content.
- `.aux` files in `Volume_I/chapters/` are LaTeX build artifacts and can be regenerated.
