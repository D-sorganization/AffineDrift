# Tangent Hyperplane Framework - PDF Versions

This folder contains PDF versions of the 4-part Tangent Hyperplane series, rendered with Quarto and XeLaTeX for proper mathematical equation display.

## Files

| File | Description |
|------|-------------|
| **Part1_Unified_Thesis.pdf** | Core document covering Geometry (Part I), Integration (Part II), and Optimization (Part III) |
| **Part2_Residual_Aware_Control.pdf** | Advanced: Quantitative residual bounds for adaptive control switching |
| **Part3_Contraction_Theory.pdf** | Advanced: Duality between contraction analysis and trajectory optimization |
| **Part4_Hybrid_Systems.pdf** | Advanced: Extension to hybrid systems with impacts, friction, and mode switches |

## Usage

These PDFs are suitable for:
- Reading offline
- Printing
- Uploading to NotebookLM or similar AI tools
- Academic reference

## Source Files

The source `.qmd` (Quarto Markdown) files are located in the parent directory:
- `Tangent_Hyperplanes_Unified_Thesis.qmd` (Part 1)
- `Advanced/Residual-Aware_Control.qmd` (Part 2)
- `Advanced/Contraction_Tangent_Unification.qmd` (Part 3)
- `Advanced/Hybrid_Tangent_Spaces.qmd` (Part 4)

## Regenerating PDFs

To regenerate the PDFs, install Quarto and TinyTeX:

```bash
# Install Quarto (https://quarto.org/docs/get-started/)
# Install TinyTeX
quarto install tinytex

# Render all articles
cd "articles/Tangent Hyperplane Articles"
quarto render Tangent_Hyperplanes_Unified_Thesis.qmd --to pdf

cd Advanced
quarto render Residual-Aware_Control.qmd --to pdf
quarto render Contraction_Tangent_Unification.qmd --to pdf
quarto render Hybrid_Tangent_Spaces.qmd --to pdf
```

---
*Generated: January 19, 2026*
