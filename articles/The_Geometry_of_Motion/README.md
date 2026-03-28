# The Geometry of Motion

Canonical LaTeX manuscript source for the six-volume textbook series *The Geometry of Motion*.

## Volumes

| Volume | Title | Chapters |
|--------|-------|----------|
| **0** | Mathematical Foundations | Linear algebra through Lagrangian mechanics and machine learning |
| **I** | Control Theory | Variational analysis, superposition, contraction, optimal control, duality |
| **II** | Trajectory and Motor Control | Orbital stability, underactuation, trajectory optimization, stochastic control |
| **III** | Biomechanics | Musculoskeletal modeling, muscle models, inverse problems, experimental methods |
| **IV** | Neural Control | Degrees-of-freedom problem, neural architecture, internal models, motor learning |
| **V** | Simulation | Engine comparison, model building, trajectory optimization, reinforcement learning |

## Directory Structure

```
The_Geometry_of_Motion/
├── Volume_0/               — Mathematical Foundations (LaTeX source)
├── Volume_I/               — Control Theory (LaTeX source)
├── Volume_II/              — Trajectory and Motor Control (LaTeX source)
├── Volume_III/             — Biomechanics (LaTeX source)
├── Volume_IV/              — Neural Control (LaTeX source)
├── Volume_V/               — Simulation (LaTeX source)
├── quarto/                 — Website mirror (Quarto .qmd files)
├── geometry_of_motion.bib  — Shared bibliography
├── geometry_of_motion.sty  — Shared LaTeX style
└── compile_series.bat      — Build script for full series
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
