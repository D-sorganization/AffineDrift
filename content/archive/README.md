# Content Archive

This directory contains archived content that has been moved from active use but is preserved for reference and potential recovery.

## Archive Structure

```
archive/
├── duplicates/              # Duplicate articles (canonical versions in articles/)
│   ├── affine-background-articles/
│   └── affine-nature-golf-swing/
├── source/                  # LaTeX source files (.tex)
│   ├── affine-background-articles/
│   └── affine-nature-golf-swing/
└── drafts/                  # Draft articles and work-in-progress
```

## What Was Archived and Why

### Duplicates (Moved: 2025-01-26)

These articles were duplicates of files in the `articles/` directory. The canonical versions are in `articles/`, and these were archived to avoid confusion.

#### From `content/Affine Background Articles/`:
- `Force_Mobility_Matrices.qmd` → Duplicate of `articles/force-mobility-matrices.qmd`
- `Inverse_Dynamics_Inference.qmd` → Duplicate of `articles/inverse-dynamics-inference.qmd`
- `Lagrangian_Reference.qmd` → Duplicate of `articles/lagrangian-reference.qmd`
- `Nonlinear_Control_Insights.qmd` → Duplicate of `articles/nonlinear-control-insights.qmd`
- `null_space_constraint_jacobian.qmd` → Duplicate of `articles/null-space-constraint-jacobian.qmd`
- `ScrewTheory_Reference.qmd` → Duplicate of `articles/screw-theory-reference.qmd`

#### From `content/Affine Nature of the Golf Swing/`:
- `A_Nonlinear_Control_Insights.qmd` → Duplicate of `articles/nonlinear-control-insights.qmd`
- `B_Inverse_Dynamics_Inference.qmd` → Duplicate of `articles/inverse-dynamics-inference.qmd`
- `C_Applications.qmd` → Duplicate of `articles/appendix-applications.qmd`
- `D_Lagrangian_Reference.qmd` → Duplicate of `articles/lagrangian-reference.qmd`
- `E_ScrewTheory_Reference.qmd` → Duplicate of `articles/screw-theory-reference.qmd`

### Source Files (Moved: 2025-01-26)

LaTeX source files (`.tex`) were moved to `archive/source/` to separate source material from published Quarto articles. The published versions are in `articles/` as `.qmd` files.

### Drafts (Moved: 2025-01-26)

- `Draft3_Compiled_Working_Copy.qmd` → Moved from `content/Affine Nature of the Golf Swing/` as it was a draft version

## Recovery

If you need to recover any archived file:

1. **To restore a duplicate**: Copy from `archive/duplicates/` back to the original location
2. **To use a source file**: The `.tex` files in `archive/source/` can be converted to `.qmd` using the tools in `tools/`
3. **To continue a draft**: Copy from `archive/drafts/` to `articles/` when ready to publish

## Notes

- All archived files are preserved in git history
- Nothing has been deleted - only moved
- The canonical versions of all articles are in the `articles/` directory
- Source files are kept for reference and potential future conversion

