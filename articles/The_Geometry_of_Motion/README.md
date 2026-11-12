# The Geometry of Motion

Canonical LaTeX manuscript source for the six-volume textbook series _The Geometry of Motion_.

## Volumes

| Volume | Canonical title (website and LaTeX) | Chapters |
| ------ | ----------------------------------- | -------- |
| **0**  | Volume 0: The Mathematical Primer | Linear algebra through Lagrangian mechanics and machine learning |
| **I**  | Volume I: Tangent-Space Methods for Nonlinear Control | Variational analysis, superposition, contraction, optimal control, duality |
| **II** | Volume II: Control Is Motion | Orbital stability, underactuation, trajectory optimization, stochastic control |
| **III** | Volume III: Biomechanics - Biology to Systems | Musculoskeletal modeling, muscle models, inverse problems, experimental methods |
| **IV** | Volume IV: Human Motor Control | Degrees-of-freedom problem, neural architecture, internal models, motor learning |
| **V** | Volume V: Practical Application | Engine comparison, model building, trajectory optimization, reinforcement learning |

The concordance in `books/index.qmd` is the authoritative title list for the public website.

## Directory Structure

```
The_Geometry_of_Motion/
├── Volume_0/               — Mathematical primer (LaTeX source)
├── Volume_I/               — Tangent-space methods (LaTeX source)
├── Volume_II/              — Control Is Motion (LaTeX source)
├── Volume_III/             — Biomechanics (LaTeX source)
├── Volume_IV/              — Human motor control (LaTeX source)
├── Volume_V/               — Practical application (LaTeX source)
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

## Superseded Internal Audit Notes

Bibliography and PR runbooks from an earlier sandbox review were archived under
`docs/development/archive/gom-manuscript-audit-superseded/` (Refs #5606). Do not
follow those instructions; use current CI gates and `geometry_of_motion.bib` instead.
