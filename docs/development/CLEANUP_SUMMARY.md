# Content Cleanup Summary

**Date**: 2025-01-26  
**Branch**: `fix/equation-rendering-and-footer`

## Overview

Organized the repository structure by:

1. Identifying and archiving duplicate articles
2. Moving LaTeX source files to archive
3. Organizing drafts and archived content
4. Updating configuration files
5. Creating documentation

## Files Moved to Archive

### Duplicates Archived (11 files)

**From `content/Affine Background Articles/`:**

- `Force_Mobility_Matrices.qmd` → `content/archive/duplicates/affine-background-articles/`
- `Inverse_Dynamics_Inference.qmd` → `content/archive/duplicates/affine-background-articles/`
- `Lagrangian_Reference.qmd` → `content/archive/duplicates/affine-background-articles/`
- `Nonlinear_Control_Insights.qmd` → `content/archive/duplicates/affine-background-articles/`
- `null_space_constraint_jacobian.qmd` → `content/archive/duplicates/affine-background-articles/`
- `ScrewTheory_Reference.qmd` → `content/archive/duplicates/affine-background-articles/`

**From `content/Affine Nature of the Golf Swing/`:**

- `A_Nonlinear_Control_Insights.qmd` → `content/archive/duplicates/affine-nature-golf-swing/`
- `B_Inverse_Dynamics_Inference.qmd` → `content/archive/duplicates/affine-nature-golf-swing/`
- `C_Applications.qmd` → `content/archive/duplicates/affine-nature-golf-swing/`
- `D_Lagrangian_Reference.qmd` → `content/archive/duplicates/affine-nature-golf-swing/`
- `E_ScrewTheory_Reference.qmd` → `content/archive/duplicates/affine-nature-golf-swing/`

**Canonical versions remain in `articles/`:**

- `articles/force-mobility-matrices.qmd`
- `articles/inverse-dynamics-inference.qmd`
- `articles/lagrangian-reference.qmd`
- `articles/nonlinear-control-insights.qmd`
- `articles/null-space-constraint-jacobian.qmd`
- `articles/screw-theory-reference.qmd`
- `articles/appendix-applications.qmd`

### Source Files Archived (12 .tex files)

**From `content/Affine Background Articles/`:**

- `Force_Mobility_Matrices.tex` → `content/archive/source/affine-background-articles/`
- `Inverse_Dynamics_Inference.tex` → `content/archive/source/affine-background-articles/`
- `Lagrangian_Reference.tex` → `content/archive/source/affine-background-articles/`
- `Nonlinear_Control_Insights.tex` → `content/archive/source/affine-background-articles/`
- `null_space_constraint_jacobian.tex` → `content/archive/source/affine-background-articles/`
- `ScrewTheory_Reference.tex` → `content/archive/source/affine-background-articles/`

**From `content/Affine Nature of the Golf Swing/`:**

- `Appendix_A_Nonlinear_Control_Insights.tex` → `content/archive/source/affine-nature-golf-swing/`
- `Appendix_B_Inverse_Dynamics_Inference.tex` → `content/archive/source/affine-nature-golf-swing/`
- `Appendix_C_Applications.tex` → `content/archive/source/affine-nature-golf-swing/`
- `Appendix_D_Lagrangian_Reference.tex` → `content/archive/source/affine-nature-golf-swing/`
- `Appendix_E_ScrewTheory_Reference.tex` → `content/archive/source/affine-nature-golf-swing/`
- `Draft3_Compiled_Working_Copy.tex` → `content/archive/source/affine-nature-golf-swing/`

### Drafts Archived (1 file)

- `Draft3_Compiled_Working_Copy.qmd` → `content/archive/drafts/`

## Configuration Changes

### `_quarto.yml`

- Removed `content/Affine Nature of the Golf Swing/*.qmd` from render list (folder now empty)
- Kept `content/Affine Background Articles/*.qmd` (still contains `Controllability_Drift_Ratio.qmd`)

## Documentation Created

1. **`content/archive/README.md`** - Documents what was archived and why, plus recovery instructions
2. **`content/README.md`** - Explains the content directory structure
3. **`FOLDER_STRUCTURE_ANALYSIS.md`** - Analysis of folder structure (created earlier)
4. **`CLEANUP_SUMMARY.md`** - This file

## Current Structure

### Active Published Articles

All published articles are in: **`articles/`** (16 files)

### Active Content Folders

- `content/Affine Background Articles/` - Contains `Controllability_Drift_Ratio.qmd`
- `content/Double Pendulum Articles/` - Contains specialized article
- `content/Strokes Gained Limitations/` - Contains specialized article
- `content/Inverse Dynamics Analysis/` - Contains analysis materials
- `content/Wrist as Universal Joint/` - Contains wrist analysis materials
- `content/WSCG2024/` - Contains conference materials

### Archive Structure

```
content/archive/
├── duplicates/              # 11 duplicate .qmd files
│   ├── affine-background-articles/ (6 files)
│   └── affine-nature-golf-swing/ (5 files)
├── source/                   # 12 LaTeX source files
│   ├── affine-background-articles/ (6 files)
│   └── affine-nature-golf-swing/ (6 files)
└── drafts/                   # 1 draft file
    └── Draft3_Compiled_Working_Copy.qmd
```

## Benefits

1. **Clear structure**: Published articles are clearly in `articles/`
2. **No duplicates**: Canonical versions are obvious
3. **Nothing lost**: All files preserved in archive
4. **Easy recovery**: Archive is well-documented
5. **Better organization**: Source files, drafts, and duplicates are separated

## Next Steps

1. Review the changes
2. Test that articles still render correctly: `quarto render`
3. Commit the cleanup changes
4. Consider moving remaining specialized articles to `articles/` if they should be published

## Notes

- All moves were done with `git mv` to preserve history
- Nothing was deleted - only moved to archive
- The `content/Affine Nature of the Golf Swing/` folder is now empty and can be removed if desired
- The archive preserves the original folder structure for easy reference
